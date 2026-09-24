#!/usr/bin/env python3
"""
camara.py  —  Se ejecuta en el Raspberry Pi 3 B que tiene la webcam.

Qué hace:
  1. Cada 10 minutos (configurable) saca una foto con la webcam USB.
  2. La guarda en su carpeta local ("su propia nube"): carpeta_local.
     El nombre es:  padron<PADRON>_DDMMAAAA_HHMMSS.jpg
  3. Sube la foto al servidor web para que el otro Raspberry la pueda descargar.
  4. Si el servidor no responde, la foto queda guardada localmente y se
     reintenta subirla en el próximo ciclo (no se pierde ninguna).
  5. "Self-check": si el Pi se apaga y se prende, systemd vuelve a lanzar
     este programa automáticamente y sigue trabajando desde donde quedó
     (las fotos que no se pudieron subir se detectan y se suben).

Requisitos en el Pi:
    sudo apt install fswebcam python3-requests
"""

import os
import sys
import time
import subprocess
from datetime import datetime

# Permite importar comun.py que está en la carpeta de arriba
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from comun import cargar_config, configurar_logging, asegurar_carpeta

import requests

log = configurar_logging("camara")

# Carpeta donde se anotan las fotos que ya se subieron con éxito
ARCHIVO_SUBIDAS = ".subidas.txt"


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


def subir_foto(url_servidor, carpeta, nombre):
    """Sube una foto al servidor. Devuelve True si se subió bien."""
    ruta = os.path.join(carpeta, nombre)
    url = url_servidor.rstrip("/") + "/subir"
    try:
        with open(ruta, "rb") as f:
            archivos = {"foto": (nombre, f, "image/jpeg")}
            r = requests.post(url, files=archivos, timeout=30)
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
    for nombre in sorted(os.listdir(carpeta)):
        if not nombre.lower().endswith(".jpg"):
            continue
        if nombre in subidas:
            continue
        if subir_foto(url_servidor, carpeta, nombre):
            marcar_subida(carpeta, nombre)


def obtener_intervalo(url_servidor, por_defecto):
    """Pregunta al servidor el intervalo configurado desde la IHM.

    Así el usuario puede cambiar el intervalo desde la interfaz gráfica sin
    reiniciar nada. Si el servidor no responde, usa el valor por defecto.
    """
    url = url_servidor.rstrip("/") + "/config"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            valor = int(r.json().get("intervalo_camara", por_defecto))
            return max(5, valor)  # mínimo 5 s por seguridad
    except (requests.RequestException, ValueError, TypeError):
        pass
    return por_defecto


def main():
    config = cargar_config()
    padron = config["general"]["padron"]
    intervalo = config.getint("camara", "intervalo_segundos")
    dispositivo = config["camara"]["dispositivo"]
    resolucion = config["camara"]["resolucion"]
    carpeta = asegurar_carpeta(config["camara"]["carpeta_local"])
    url_servidor = config["camara"]["url_servidor"]

    log.info("Cámara iniciada. Padrón=%s  Intervalo=%ss  Carpeta=%s",
             padron, intervalo, carpeta)

    # Al arrancar (incluso después de un reinicio) intenta subir lo pendiente.
    subir_pendientes(url_servidor, carpeta)

    while True:
        inicio = time.time()

        nombre = nombre_foto(padron)
        ruta = os.path.join(carpeta, nombre)

        if sacar_foto(dispositivo, resolucion, ruta):
            log.info("Foto guardada: %s", ruta)
            if subir_foto(url_servidor, carpeta, nombre):
                marcar_subida(carpeta, nombre)
        else:
            log.error("No se pudo sacar la foto en este ciclo.")

        # Reintenta subir cualquier foto vieja que quedó pendiente.
        subir_pendientes(url_servidor, carpeta)

        # Espera hasta completar el intervalo. Lo revisa en pasos cortos para
        # tomar al vuelo un cambio hecho desde la IHM (sin reiniciar la cámara).
        objetivo = obtener_intervalo(url_servidor, intervalo)
        log.info("Próxima foto en ~%d segundos...", objetivo)
        while (time.time() - inicio) < objetivo:
            time.sleep(min(5, objetivo))
            objetivo = obtener_intervalo(url_servidor, intervalo)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log.info("Cámara detenida por el usuario.")
