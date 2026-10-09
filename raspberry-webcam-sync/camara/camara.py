#!/usr/bin/env python3
"""
camara.py  —  Se ejecuta en el Raspberry Pi 3 B que tiene la webcam.

Qué hace:
  1. Arranca solo al prender el Pi, pero queda EN ESPERA: no saca fotos
     hasta que desde la IHM se aprieta "Iniciar captura". Con "Detener"
     vuelve a quedar en espera (el programa sigue corriendo).
  2. Mientras captura, cada 10 minutos (configurable) saca una foto con la
     webcam USB y le pide al Arduino (piranómetro) la medición del sol.
  3. Guarda la foto en su carpeta local ("su propia nube"): carpeta_local,
     y la medición en carpeta_local/mediciones.csv (misma fila = misma foto).
     El nombre es:  padron<PADRON>_DDMMAAAA_HHMMSS.jpg
  4. Sube la foto + su medición al servidor web para que el otro Raspberry
     las pueda descargar.
  5. Si el servidor no responde, la foto queda guardada localmente y se
     reintenta subirla en el próximo ciclo (no se pierde ninguna).
  6. "Self-check": si el Pi se apaga y se prende, systemd vuelve a lanzar
     este programa automáticamente; las fotos que no se pudieron subir se
     detectan y se suben. (La captura vuelve a quedar en espera: hay que
     ajustar la hora e iniciar desde la IHM.)

Requisitos en el Pi:
    sudo apt install fswebcam python3-requests python3-serial
"""

import os
import sys
import csv
import json
import time
import subprocess
from datetime import datetime

# Permite importar comun.py que está en la carpeta de arriba
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from comun import cargar_config, configurar_logging, asegurar_carpeta, puerto_arduino

import requests

log = configurar_logging("camara")

# Carpeta donde se anotan las fotos que ya se subieron con éxito
ARCHIVO_SUBIDAS = ".subidas.txt"

# Mediciones del piranómetro (una fila por foto), en la carpeta local
ARCHIVO_MEDICIONES = "mediciones.csv"
COLUMNAS_MEDICIONES = [
    "nombre", "fecha_hora",
    "g_now", "g_avg", "g_min", "g_max", "g_std", "p_avg_mw", "i_avg_ma",
    "v_now", "v_avg", "v_min", "v_max", "v_std",
    "adc_now", "n_samples", "window_s", "sat", "vcc", "arduino_ok",
]

# Cada cuántos segundos se consulta al servidor (estado + intervalo) y se
# manda la lectura "en vivo" del piranómetro.
PASO_CONSULTA = 5


# ------------------------------------------------------------------
#  Arduino (piranómetro): por cable USB o por los GPIO 14/15
# ------------------------------------------------------------------
class Arduino:
    """Habla con arduino/piranometro/piranometro.ino.

    Le manda "GET" (resumen desde la última foto, y reinicia) o "NOW"
    (lectura del momento, sin reiniciar) y recibe UNA línea JSON.
    Si el Arduino no está conectado, devuelve None y la cámara sigue
    sacando fotos igual.
    """

    def __init__(self, puerto, baudios):
        self.puerto = puerto
        self.baudios = baudios
        self.serie = None

    def consultar(self, comando="GET", espera=3.0):
        try:
            if self.serie is None:
                import serial  # python3-serial
                # "auto" se resuelve en cada apertura: si se enchufa o se
                # desenchufa el USB, la próxima consulta usa el puerto que haya.
                puerto = puerto_arduino(self.puerto)
                self.serie = serial.Serial(puerto, self.baudios, timeout=0.3)
                # Por USB, abrir el puerto REINICIA el Arduino UNO: se espera
                # a que arranque y se descarta su mensaje de bienvenida.
                time.sleep(2.5)
                self.serie.reset_input_buffer()
                log.info("Arduino conectado en %s", puerto)
            self.serie.reset_input_buffer()
            self.serie.write((comando + "\n").encode("ascii"))
            limite = time.monotonic() + espera
            buffer = b""
            while time.monotonic() < limite:
                buffer += self.serie.read(self.serie.in_waiting or 1)
                while b"\n" in buffer:
                    linea, buffer = buffer.split(b"\n", 1)
                    linea = linea.strip()
                    if linea.startswith(b"{") and linea.endswith(b"}"):
                        return json.loads(linea)
            if comando == "GET":   # el "NOW" cada 5 s no llena el log
                log.warning("El Arduino no respondió a %s.", comando)
        except Exception as e:   # puerto ausente, JSON roto, cable suelto...
            if comando == "GET":
                log.warning("Error con el Arduino (%s): %s", puerto_arduino(self.puerto), e)
            try:
                if self.serie is not None:
                    self.serie.close()
            except Exception:
                pass
            self.serie = None   # se reabre en el próximo intento
        return None


class SinArduino:
    """Reemplazo cuando el Arduino está deshabilitado en config.ini."""

    def consultar(self, comando="GET", espera=0):
        return None


def nombre_foto(padron):
    """Genera el nombre de la foto: padron<PADRON>_DDMMAAAA_HHMMSS.jpg"""
    ahora = datetime.now()
    fecha = ahora.strftime("%d%m%Y")   # ddmmaaaa
    hora = ahora.strftime("%H%M%S")    # para no repetir nombre (144 fotos/día)
    return f"padron{padron}_{fecha}_{hora}.jpg"


def sacar_foto(dispositivo, resolucion, ruta_destino):
    """Saca una foto con fswebcam y la guarda en ruta_destino. Devuelve True/False."""
    comando = [
        "fswebcam",
        "-d", dispositivo,
        "-r", resolucion,
        "--no-banner",       # sin la barra negra con fecha encima de la imagen
        ruta_destino,
    ]
    try:
        resultado = subprocess.run(
            comando, capture_output=True, text=True, timeout=30
        )
        if resultado.returncode == 0 and os.path.exists(ruta_destino) \
                and os.path.getsize(ruta_destino) > 0:
            return True
        log.error("fswebcam falló: %s", resultado.stderr.strip())
        return False
    except FileNotFoundError:
        log.error("No está instalado 'fswebcam'. Instalá con: sudo apt install fswebcam")
        return False
    except subprocess.TimeoutExpired:
        log.error("La webcam no respondió a tiempo.")
        return False


# ------------------------------------------------------------------
#  Mediciones (CSV local)
# ------------------------------------------------------------------
def guardar_medicion(carpeta, nombre, datos):
    """Agrega la fila de la foto a mediciones.csv y devuelve la fila."""
    fila = {c: "" for c in COLUMNAS_MEDICIONES}
    fila.update({k: v for k, v in (datos or {}).items() if k in fila})
    fila["nombre"] = nombre
    fila["fecha_hora"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fila["arduino_ok"] = 1 if datos else 0
    ruta = os.path.join(carpeta, ARCHIVO_MEDICIONES)
    nuevo = not os.path.exists(ruta)
    with open(ruta, "a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNAS_MEDICIONES)
        if nuevo:
            w.writeheader()
        w.writerow(fila)
    return fila


def leer_mediciones(carpeta):
    """{nombre_foto: fila} de mediciones.csv (para re-subir pendientes)."""
    ruta = os.path.join(carpeta, ARCHIVO_MEDICIONES)
    if not os.path.exists(ruta):
        return {}
    with open(ruta, "r", encoding="utf-8", newline="") as f:
        return {fila["nombre"]: fila for fila in csv.DictReader(f)}


# ------------------------------------------------------------------
#  Subida al servidor
# ------------------------------------------------------------------
def cargar_lista_subidas(carpeta):
    ruta = os.path.join(carpeta, ARCHIVO_SUBIDAS)
    if not os.path.exists(ruta):
        return set()
    with open(ruta, "r", encoding="utf-8") as f:
        return set(linea.strip() for linea in f if linea.strip())


def marcar_subida(carpeta, nombre):
    ruta = os.path.join(carpeta, ARCHIVO_SUBIDAS)
    with open(ruta, "a", encoding="utf-8") as f:
        f.write(nombre + "\n")


def subir_foto(url_servidor, carpeta, nombre, medicion=None):
    """Sube una foto (y su medición, si hay) al servidor. True si salió bien."""
    ruta = os.path.join(carpeta, nombre)
    url = url_servidor.rstrip("/") + "/subir"
    datos = {"medicion": json.dumps(medicion)} if medicion else {}
    try:
        with open(ruta, "rb") as f:
            archivos = {"foto": (nombre, f, "image/jpeg")}
            r = requests.post(url, files=archivos, data=datos, timeout=30)
        if r.status_code == 200:
            log.info("Subida OK: %s", nombre)
            return True
        log.warning("El servidor respondió %s al subir %s", r.status_code, nombre)
        return False
    except requests.RequestException as e:
        log.warning("No se pudo subir %s (servidor no disponible): %s", nombre, e)
        return False


def subir_pendientes(url_servidor, carpeta):
    """Sube todas las fotos locales que todavía no se subieron (recuperación)."""
    subidas = cargar_lista_subidas(carpeta)
    pendientes = [n for n in sorted(os.listdir(carpeta))
                  if n.lower().endswith(".jpg") and n not in subidas]
    if not pendientes:
        return
    mediciones = leer_mediciones(carpeta)
    for nombre in pendientes:
        if subir_foto(url_servidor, carpeta, nombre, mediciones.get(nombre)):
            marcar_subida(carpeta, nombre)


def consultar_servidor(url_servidor, por_defecto):
    """Pregunta al servidor el intervalo y si hay que estar capturando.

    Así el usuario controla la cámara desde la IHM sin reiniciar nada.
    Devuelve (intervalo, capturando). Si el servidor no responde, sigue
    con el intervalo por defecto y NO captura (en espera).
    La consulta también le sirve al servidor como "latido" de la cámara.
    """
    url = url_servidor.rstrip("/") + "/config"
    try:
        r = requests.get(url, params={"origen": "camara"}, timeout=10)
        if r.status_code == 200:
            datos = r.json()
            valor = int(datos.get("intervalo_camara", por_defecto))
            return max(5, valor), bool(datos.get("capturando", False))  # mínimo 5 s
    except (requests.RequestException, ValueError, TypeError):
        pass
    return por_defecto, False


def enviar_sensor_vivo(url_servidor, arduino):
    """Manda al servidor la lectura del momento del piranómetro (para la IHM)."""
    datos = arduino.consultar("NOW", espera=2.0)
    if not datos:
        return
    try:
        requests.post(url_servidor.rstrip("/") + "/sensor", json=datos, timeout=5)
    except requests.RequestException:
        pass


def ciclo_de_foto(padron, dispositivo, resolucion, carpeta, url_servidor, arduino):
    """Saca UNA foto con su medición, la guarda y la sube."""
    nombre = nombre_foto(padron)
    ruta = os.path.join(carpeta, nombre)

    # Primero la medición: resume el sol desde la foto anterior hasta ahora.
    medicion = arduino.consultar("GET")

    if sacar_foto(dispositivo, resolucion, ruta):
        fila = guardar_medicion(carpeta, nombre, medicion)
        log.info("Foto guardada: %s  (radiación media: %s W/m²)",
                 ruta, fila.get("g_avg") or "sin dato")
        if subir_foto(url_servidor, carpeta, nombre, fila):
            marcar_subida(carpeta, nombre)
    else:
        log.error("No se pudo sacar la foto en este ciclo.")

    # Reintenta subir cualquier foto vieja que quedó pendiente.
    subir_pendientes(url_servidor, carpeta)


def main():
    config = cargar_config()
    padron = config["general"]["padron"]
    intervalo = config.getint("camara", "intervalo_segundos")
    dispositivo = config["camara"]["dispositivo"]
    resolucion = config["camara"]["resolucion"]
    carpeta = asegurar_carpeta(config["camara"]["carpeta_local"])
    url_servidor = config["camara"]["url_servidor"]

    if config.getboolean("arduino", "habilitado", fallback=False):
        arduino = Arduino(config["arduino"].get("puerto", "auto"),
                          config.getint("arduino", "baudios", fallback=9600))
    else:
        arduino = SinArduino()

    log.info("Cámara iniciada EN ESPERA. Padrón=%s  Intervalo=%ss  Carpeta=%s",
             padron, intervalo, carpeta)

    # Al arrancar (incluso después de un reinicio) intenta subir lo pendiente.
    subir_pendientes(url_servidor, carpeta)

    # Se usa time.monotonic() (y no la hora del reloj) para medir los
    # intervalos: así, ajustar la fecha/hora desde la IHM en medio de una
    # captura no adelanta ni atrasa la próxima foto.
    proxima = None          # cuándo sacar la próxima foto (None = en espera)
    capturando_antes = False
    while True:
        objetivo, capturando = consultar_servidor(url_servidor, intervalo)

        if capturando and not capturando_antes:
            log.info("Captura INICIADA desde la IHM (cada %d s).", objetivo)
            proxima = time.monotonic()            # la primera foto, ya
        elif not capturando and capturando_antes:
            log.info("Captura DETENIDA desde la IHM. En espera...")
            proxima = None
        capturando_antes = capturando

        if capturando and time.monotonic() >= proxima:
            inicio = time.monotonic()
            ciclo_de_foto(padron, dispositivo, resolucion, carpeta,
                          url_servidor, arduino)
            proxima = inicio + objetivo
            log.info("Próxima foto en ~%d segundos...", objetivo)
        elif capturando and proxima - time.monotonic() > objetivo:
            # Achicaron el intervalo desde la IHM: se aplica ya.
            proxima = time.monotonic() + objetivo

        enviar_sensor_vivo(url_servidor, arduino)

        espera = PASO_CONSULTA
        if capturando:
            espera = max(0.5, min(PASO_CONSULTA, proxima - time.monotonic()))
        time.sleep(espera)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log.info("Cámara detenida por el usuario.")
