#!/usr/bin/env python3
"""
servidor.py  —  La "nube". Corre en el Pi de la cámara (o donde quieras).

Qué hace:
  - Recibe las fotos que sube el Pi de la cámara (endpoint /subir).
  - Guarda TODAS las fotos en carpeta_nube.
  - Muestra una página web con:
      * un PANEL DE ESTADO gráfico (luces 🟢/🔴) que confirma si el servidor,
        la cámara y el descargador están funcionando;
      * la lista de fotos AGRUPADA POR DÍA;
      * botones para descargar una foto, o todas en un ZIP.
  - La página se auto-refresca sola cada 30 segundos.
  - Recibe "latidos" del descargador (/latido) para saber si está vivo.
  - Controla si la cámara está CAPTURANDO o EN ESPERA (/captura). Al
    prender el Pi siempre arranca EN ESPERA: recién saca fotos cuando la
    IHM manda "Iniciar".
  - Permite AJUSTAR LA FECHA Y HORA del Pi desde la IHM (/hora), porque
    el Pi no tiene internet ni pila de reloj.
  - Guarda la medición del piranómetro (Arduino) de cada foto en
    mediciones.csv (descargable en /mediciones.csv).

Requisitos en el equipo servidor:
    sudo apt install python3-flask

Cómo probar desde un navegador:
    http://IP_DEL_SERVIDOR:8000
"""

import io
import os
import re
import sys
import csv
import json
import time
import zipfile
import tempfile
import subprocess
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from comun import cargar_config, configurar_logging, asegurar_carpeta

from flask import (
    Flask, request, send_from_directory, send_file, jsonify,
    render_template_string, abort, Response,
)
from werkzeug.utils import secure_filename

log = configurar_logging("servidor")

config = cargar_config()
CARPETA_NUBE = asegurar_carpeta(config["servidor"]["carpeta_nube"])
PUERTO = config.getint("servidor", "puerto")
# Umbrales para decidir si algo está "activo" (2 ciclos + un margen).
INTERVALO_CAMARA = config.getint("camara", "intervalo_segundos", fallback=600)
INTERVALO_DESCARGA = config.getint("descargador", "intervalo_segundos", fallback=300)
# Para el "Ver en vivo": misma webcam que la cámara. Resolución baja = más fluido.
DISPOSITIVO = config["camara"].get("dispositivo", "/dev/video0")
RES_LIVE = config["camara"].get("resolucion_vivo", "640x480")

# --- Configuración en caliente (la IHM puede cambiar intervalo y captura) ---
# Se guarda en un archivo para que sobreviva a reinicios del servidor.
ARCHIVO_ESTADO = os.path.join(CARPETA_NUBE, ".config_runtime.json")
INTERVALO_MIN = 5
INTERVALO_MAX = 86400  # 1 día

# Mediciones del piranómetro: una fila por foto.
ARCHIVO_MEDICIONES = os.path.join(CARPETA_NUBE, "mediciones.csv")
COLUMNAS_MEDICIONES = [
    "nombre", "fecha_hora",
    "g_now", "g_avg", "g_min", "g_max", "g_std", "p_avg_mw", "i_avg_ma",
    "v_now", "v_avg", "v_min", "v_max", "v_std",
    "adc_now", "n_samples", "window_s", "sat", "vcc", "arduino_ok",
]

# Año mínimo aceptado al ajustar la hora (evita mandar una fecha basura).
EPOCH_MINIMO = 1704067200  # 01/01/2024


def id_arranque():
    """Identificador único de ESTE encendido del Pi (cambia en cada reinicio)."""
    try:
        with open("/proc/sys/kernel/random/boot_id", "r", encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return "desconocido"


def leer_runtime():
    """Estado en caliente completo (dict). Nunca falla: si no hay, vacío."""
    try:
        with open(ARCHIVO_ESTADO, "r", encoding="utf-8") as f:
            datos = json.load(f)
            return datos if isinstance(datos, dict) else {}
    except (OSError, ValueError):
        return {}


def guardar_runtime(**cambios):
    """Actualiza solo las claves indicadas del estado en caliente."""
    datos = leer_runtime()
    datos.update(cambios)
    with open(ARCHIVO_ESTADO, "w", encoding="utf-8") as f:
        json.dump(datos, f)
    return datos


def leer_intervalo_camara():
    """Intervalo actual de la cámara (segundos). Del archivo, o del config.ini."""
    try:
        return int(leer_runtime()["intervalo_camara"])
    except (KeyError, ValueError, TypeError):
        return INTERVALO_CAMARA


def guardar_intervalo_camara(valor):
    """Guarda el nuevo intervalo (validado) en el archivo de estado."""
    valor = max(INTERVALO_MIN, min(INTERVALO_MAX, int(valor)))
    guardar_runtime(intervalo_camara=valor)
    return valor


def leer_capturando():
    """True si la cámara tiene que sacar fotos; False si está en espera."""
    return bool(leer_runtime().get("capturando", False))


def hora_ajustada():
    """True si la hora se ajustó desde la IHM en ESTE encendido del Pi."""
    return leer_runtime().get("hora_ajustada_arranque") == id_arranque()


def ajustar_hora_sistema(epoch):
    """Pone el reloj del Pi en 'epoch' (segundos UTC).

    Necesita la regla de sudo que instala scripts/instalar_servidor.sh
    (solo permite 'date' y 'fake-hwclock', sin contraseña).
    """
    subprocess.run(["sudo", "-n", "date", "-u", "-s", f"@{epoch:.0f}"],
                   check=True, capture_output=True, text=True, timeout=10)
    # fake-hwclock guarda la hora en disco: tras un reinicio el reloj
    # vuelve al menos a esta hora (igual conviene volver a ajustarlo).
    subprocess.run(["sudo", "-n", "fake-hwclock", "save", "force"],
                   capture_output=True, timeout=10)


def nombres_con_medicion():
    """Nombres de fotos que ya tienen su fila en mediciones.csv."""
    try:
        with open(ARCHIVO_MEDICIONES, "r", encoding="utf-8", newline="") as f:
            return {fila.get("nombre") for fila in csv.DictReader(f)}
    except OSError:
        return set()


def guardar_medicion(nombre, medicion):
    """Agrega la fila de la foto a mediciones.csv (sin duplicar)."""
    if nombre in nombres_con_medicion():
        return
    nuevo = not os.path.exists(ARCHIVO_MEDICIONES)
    fila = dict(medicion)
    fila["nombre"] = nombre
    with open(ARCHIVO_MEDICIONES, "a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNAS_MEDICIONES,
                           restval="", extrasaction="ignore")
        if nuevo:
            w.writeheader()
        w.writerow(fila)


# Al arrancar el servidor (o sea, al prender el Pi) la cámara queda EN
# ESPERA: no saca fotos hasta que la IHM mande "Iniciar".
guardar_runtime(capturando=False)

app = Flask(__name__)

# Guarda cuándo fue el último "latido" de cada componente (en memoria).
ultimo_latido = {}

# Última lectura "en vivo" del piranómetro que mandó la cámara.
sensor_vivo = {"datos": None, "cuando": None}

RE_FECHA = re.compile(r"_(\d{8})_")


def fecha_de_nombre(nombre):
    m = RE_FECHA.search(nombre)
    return m.group(1) if m else "sin_fecha"


def hace_cuanto(segundos):
    """Convierte segundos en un texto tipo 'hace 3 min'."""
    if segundos is None:
        return "nunca"
    segundos = int(segundos)
    if segundos < 60:
        return f"hace {segundos} s"
    if segundos < 3600:
        return f"hace {segundos // 60} min"
    return f"hace {segundos // 3600} h"


def listar_fotos():
    fotos = []
    for nombre in os.listdir(CARPETA_NUBE):
        if nombre.lower().endswith(".jpg"):
            ruta = os.path.join(CARPETA_NUBE, nombre)
            fotos.append({
                "nombre": nombre,
                "kb": round(os.path.getsize(ruta) / 1024, 1),
                "mtime": os.path.getmtime(ruta),
                "dia": fecha_de_nombre(nombre),
            })
    # Orden cronológico real (más nuevas primero).
    fotos.sort(key=lambda f: f["mtime"], reverse=True)
    return fotos


def estado_sistema(fotos):
    """Calcula el estado de servidor / cámara / descargador para el panel."""
    ahora = time.time()

    # Fotos: en base a la foto más nueva.
    if fotos:
        edad_foto = ahora - max(f["mtime"] for f in fotos)
    else:
        edad_foto = None
    intervalo = leer_intervalo_camara()
    capturando = leer_capturando()

    # Cámara: el programa consulta /config cada pocos segundos (latido).
    lat_cam = ultimo_latido.get("camara")
    camara_viva = lat_cam is not None and (ahora - lat_cam) < 60
    if capturando:
        camara_ok = edad_foto is not None and edad_foto < intervalo * 2 + 60
    else:
        camara_ok = camara_viva   # en espera: alcanza con que esté corriendo

    # Descargador: en base a su último latido.
    lat = ultimo_latido.get("descargador")
    edad_lat = (ahora - lat) if lat else None
    desc_ok = edad_lat is not None and edad_lat < INTERVALO_DESCARGA * 2 + 60

    # Piranómetro: última lectura en vivo (si es vieja, se considera caído).
    sv = sensor_vivo["datos"] if sensor_vivo["cuando"] and \
        ahora - sensor_vivo["cuando"] < 60 else None

    return {
        "servidor_ok": True,  # si estás viendo la página, el servidor anda
        "camara_ok": camara_ok,
        "camara_viva": camara_viva,
        "capturando": capturando,
        "camara_txt": hace_cuanto(edad_foto) if edad_foto is not None else "sin fotos aún",
        "desc_ok": desc_ok,
        "desc_txt": hace_cuanto(edad_lat) if edad_lat is not None else "sin conexión aún",
        "intervalo_camara": intervalo,
        "total_fotos": len(fotos),
        "hora_pi": ahora,
        "hora_pi_txt": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "hora_ajustada": hora_ajustada(),
        "sensor": sv,
    }


def agrupar_por_dia(fotos):
    """Devuelve [(dia_texto, [fotos...]), ...] ordenado de más nuevo a más viejo."""
    grupos = {}
    for f in fotos:
        grupos.setdefault(f["dia"], []).append(f)
    salida = []
    for dia in sorted(grupos.keys(), reverse=True):
        # dia = DDMMAAAA -> lo mostramos como DD/MM/AAAA
        if len(dia) == 8 and dia.isdigit():
            bonito = f"{dia[0:2]}/{dia[2:4]}/{dia[4:8]}"
        else:
            bonito = dia
        salida.append((bonito, grupos[dia]))
    return salida


PAGINA = """
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="refresh" content="30">
  <title>Nube de fotos - Webcam Raspberry Pi</title>
  <style>
    body { font-family: system-ui, sans-serif; margin: 1.5rem; background:#0f1115; color:#e6e6e6; }
    h1 { font-size: 1.4rem; }
    a { color:#6cb6ff; }
    .panel { display:flex; flex-wrap:wrap; gap:.8rem; margin:1rem 0; }
    .tarjeta { background:#161a22; border:1px solid #2a2f3a; border-radius:12px;
               padding:.7rem 1rem; min-width:150px; }
    .tarjeta .titulo { font-size:.8rem; color:#9aa4b2; text-transform:uppercase; letter-spacing:.04em; }
    .tarjeta .valor { font-size:1rem; margin-top:.25rem; display:flex; align-items:center; gap:.5rem; }
    .dot { width:12px; height:12px; border-radius:50%; display:inline-block; }
    .ok { background:#22c55e; box-shadow:0 0 8px #22c55e; }
    .mal { background:#ef4444; box-shadow:0 0 8px #ef4444; }
    .barra { margin: 1rem 0; }
    .btn { display:inline-block; background:#2563eb; color:#fff; padding:.5rem .9rem;
           border-radius:8px; text-decoration:none; }
    h2.dia { font-size:1rem; margin:1.4rem 0 .4rem; color:#cbd5e1;
             border-bottom:1px solid #2a2f3a; padding-bottom:.3rem; }
    table { border-collapse: collapse; width:100%; max-width:700px; }
    th, td { text-align:left; padding:.35rem .6rem; border-bottom:1px solid #222831; }
    .vacio { color:#9aa4b2; }
    .pie { margin-top:2rem; color:#6b7280; font-size:.8rem; }
  </style>
</head>
<body>
  <h1>📷 Nube de fotos de la webcam</h1>

  <div class="panel">
    <div class="tarjeta">
      <div class="titulo">Servidor</div>
      <div class="valor"><span class="dot {{ 'ok' if e.servidor_ok else 'mal' }}"></span>
        {{ 'Activo' if e.servidor_ok else 'Caído' }}</div>
    </div>
    <div class="tarjeta">
      <div class="titulo">Cámara</div>
      <div class="valor"><span class="dot {{ 'ok' if e.camara_ok else 'mal' }}"></span>
        {{ 'Activa' if e.camara_ok else 'Sin fotos recientes' }}</div>
      <div class="titulo" style="margin-top:.3rem">última foto {{ e.camara_txt }}</div>
    </div>
    <div class="tarjeta">
      <div class="titulo">Descargador</div>
      <div class="valor"><span class="dot {{ 'ok' if e.desc_ok else 'mal' }}"></span>
        {{ 'Conectado' if e.desc_ok else 'Sin conexión' }}</div>
      <div class="titulo" style="margin-top:.3rem">último aviso {{ e.desc_txt }}</div>
    </div>
    <div class="tarjeta">
      <div class="titulo">Captura</div>
      <div class="valor"><span class="dot {{ 'ok' if e.capturando else 'mal' }}"></span>
        {{ 'Capturando' if e.capturando else 'En espera' }}</div>
      <div class="titulo" style="margin-top:.3rem">se inicia desde la IHM</div>
    </div>
    <div class="tarjeta">
      <div class="titulo">Radiación (piranómetro)</div>
      <div class="valor"><span class="dot {{ 'ok' if e.sensor else 'mal' }}"></span>
        {% if e.sensor %}{{ e.sensor.g_now }} W/m² · {{ e.sensor.v_now }} V{% else %}Sin datos{% endif %}</div>
    </div>
    <div class="tarjeta">
      <div class="titulo">Hora del Pi</div>
      <div class="valor"><span class="dot {{ 'ok' if e.hora_ajustada else 'mal' }}"></span>
        {{ e.hora_pi_txt }}</div>
      <div class="titulo" style="margin-top:.3rem">{{ 'ajustada' if e.hora_ajustada else 'sin ajustar desde que prendió' }}</div>
    </div>
    <div class="tarjeta">
      <div class="titulo">Total fotos</div>
      <div class="valor">🖼️ {{ fotos|length }}</div>
    </div>
  </div>

  <div class="barra">
    <a class="btn" style="background:#dc2626" href="/envivo">🔴 Ver en vivo</a>
    {% if fotos %}<a class="btn" href="/descargar_todo">⬇ Descargar todas (ZIP)</a>{% endif %}
    {% if hay_mediciones %}<a class="btn" style="background:#16a34a" href="/mediciones.csv">⬇ Mediciones (CSV)</a>{% endif %}
  </div>

  {% if fotos %}
    {% for dia, lista in grupos %}
      <h2 class="dia">📅 {{ dia }} &nbsp;<span style="color:#6b7280;font-weight:normal">({{ lista|length }} fotos)</span></h2>
      <table>
        <tr><th>Foto</th><th>Tamaño</th><th>Descargar</th></tr>
        {% for f in lista %}
        <tr>
          <td>{{ f.nombre }}</td>
          <td>{{ f.kb }} KB</td>
          <td><a href="/foto/{{ f.nombre }}">⬇</a></td>
        </tr>
        {% endfor %}
      </table>
    {% endfor %}
  {% else %}
    <p class="vacio">Todavía no hay fotos. Esperando a que la cámara suba la primera...</p>
  {% endif %}

  <p class="pie">Esta página se actualiza sola cada 30 segundos.</p>
</body>
</html>
"""


PAGINA_VIVO = """
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Ver en vivo - Webcam Raspberry Pi</title>
  <style>
    body { font-family: system-ui, sans-serif; margin:1.5rem; background:#0f1115; color:#e6e6e6; text-align:center; }
    a { color:#6cb6ff; }
    img { max-width:100%; border-radius:12px; border:1px solid #2a2f3a; margin-top:1rem; background:#000; }
    .btn { display:inline-block; background:#2563eb; color:#fff; padding:.5rem .9rem; border-radius:8px; text-decoration:none; }
    .estado { color:#9aa4b2; font-size:.9rem; margin-top:.6rem; }
    .vivo { color:#f87171; font-weight:bold; }
  </style>
</head>
<body>
  <h1>🔴 <span class="vivo">EN VIVO</span> — cámara</h1>
  <p><a class="btn" href="/">← Volver a la nube</a></p>
  <img id="cam" src="/vivo" alt="Cargando imagen de la cámara...">
  <p class="estado" id="est">Actualizando cada 2 segundos...</p>
  <script>
    var img = document.getElementById('cam');
    var est = document.getElementById('est');
    function refrescar() {
      var nueva = new Image();
      nueva.onload = function() {
        img.src = nueva.src;
        est.textContent = "Última actualización: " + new Date().toLocaleTimeString();
      };
      nueva.onerror = function() {
        est.textContent = "No se pudo tomar la imagen (¿webcam ocupada?). Reintentando...";
      };
      nueva.src = "/vivo?t=" + Date.now();
    }
    setInterval(refrescar, 2000);
  </script>
</body>
</html>
"""


def capturar_live():
    """Saca una foto del momento con la webcam y devuelve su ruta (o None)."""
    salida = os.path.join(tempfile.gettempdir(), "vivo.jpg")
    cmd = ["fswebcam", "-d", DISPOSITIVO, "-r", RES_LIVE, "--no-banner", salida]
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=15)
    except (FileNotFoundError, subprocess.TimeoutExpired) as ex:
        log.warning("Live view: %s", ex)
        return None
    if r.returncode == 0 and os.path.exists(salida) and os.path.getsize(salida) > 0:
        return salida
    return None


@app.route("/")
def inicio():
    fotos = listar_fotos()
    return render_template_string(
        PAGINA, fotos=fotos, e=estado_sistema(fotos), grupos=agrupar_por_dia(fotos),
        hay_mediciones=os.path.exists(ARCHIVO_MEDICIONES),
    )


@app.route("/envivo")
def envivo():
    """Página con la imagen en vivo que se refresca sola."""
    return render_template_string(PAGINA_VIVO)


@app.route("/vivo")
def vivo():
    """Devuelve una foto tomada en este instante (no se guarda en la nube)."""
    ruta = capturar_live()
    if not ruta:
        abort(503, "No se pudo capturar la imagen en vivo "
                   "(¿webcam ocupada o fswebcam no instalado?)")
    resp = send_file(ruta, mimetype="image/jpeg")
    resp.headers["Cache-Control"] = "no-store, must-revalidate"
    return resp


@app.route("/subir", methods=["POST"])
def subir():
    """La cámara sube acá cada foto."""
    if "foto" not in request.files:
        abort(400, "Falta el archivo 'foto'")
    archivo = request.files["foto"]
    nombre = secure_filename(archivo.filename or "")
    if not nombre.lower().endswith(".jpg"):
        abort(400, "Solo se aceptan archivos .jpg")
    destino = os.path.join(CARPETA_NUBE, nombre)
    archivo.save(destino)
    ultimo_latido["camara"] = time.time()

    # Medición del piranómetro que acompaña a la foto (campo opcional).
    crudo = request.form.get("medicion")
    if crudo:
        try:
            guardar_medicion(nombre, json.loads(crudo))
        except (ValueError, TypeError, OSError) as ex:
            log.warning("Medición inválida para %s: %s", nombre, ex)

    log.info("Foto recibida: %s (%d bytes)", nombre, os.path.getsize(destino))
    return jsonify({"ok": True, "nombre": nombre})


@app.route("/latido", methods=["POST"])
def latido():
    """Un componente (ej. el descargador) avisa que está vivo."""
    origen = request.form.get("origen", "desconocido")
    ultimo_latido[origen] = time.time()
    return jsonify({"ok": True})


@app.route("/config", methods=["GET", "POST"])
def config_runtime():
    """Lee (GET) o cambia (POST) el intervalo de la cámara.

    La cámara consulta esto en cada ciclo (con ?origen=camara, que sirve
    también de latido); la IHM (PyQt6) lo cambia con POST.
    """
    if request.method == "POST":
        crudo = request.form.get("intervalo_camara", request.args.get("intervalo_camara"))
        try:
            nuevo = guardar_intervalo_camara(crudo)
        except (TypeError, ValueError):
            abort(400, "Falta o es inválido 'intervalo_camara' (segundos)")
        log.info("Intervalo de la cámara cambiado a %d s (desde la IHM).", nuevo)
        return jsonify({"ok": True, "intervalo_camara": nuevo})
    if request.args.get("origen") == "camara":
        ultimo_latido["camara"] = time.time()
    return jsonify({"intervalo_camara": leer_intervalo_camara(),
                    "capturando": leer_capturando()})


@app.route("/captura", methods=["POST"])
def captura():
    """Inicia o detiene la captura de fotos (lo usa la IHM).

    Formulario: accion = iniciar | detener
    """
    accion = request.form.get("accion", "")
    if accion not in ("iniciar", "detener"):
        abort(400, "accion debe ser 'iniciar' o 'detener'")
    capturando = accion == "iniciar"
    guardar_runtime(capturando=capturando)
    log.info("Captura %s (desde la IHM).", "INICIADA" if capturando else "DETENIDA")
    return jsonify({"ok": True, "capturando": capturando})


@app.route("/hora", methods=["POST"])
def hora():
    """Ajusta la fecha y hora del Pi (lo usa la IHM).

    Formulario: epoch = segundos desde 1970 (UTC), ej. 1760000000
    """
    try:
        epoch = float(request.form["epoch"])
    except (KeyError, ValueError):
        abort(400, "Falta o es inválido 'epoch'")
    if epoch < EPOCH_MINIMO:
        abort(400, "Fecha anterior a 2024: no se acepta")
    try:
        ajustar_hora_sistema(epoch)
    except subprocess.CalledProcessError as ex:
        log.error("No se pudo ajustar la hora: %s", ex.stderr)
        return jsonify({"ok": False, "error": "sudo date falló (¿falta la regla de "
                        "sudoers? correr scripts/instalar_servidor.sh)"}), 500
    except (FileNotFoundError, subprocess.TimeoutExpired) as ex:
        return jsonify({"ok": False, "error": str(ex)}), 500
    guardar_runtime(hora_ajustada_arranque=id_arranque())
    ahora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    log.info("Hora del Pi ajustada a %s (desde la IHM).", ahora)
    return jsonify({"ok": True, "hora_pi": time.time(), "hora_pi_txt": ahora})


@app.route("/sensor", methods=["POST"])
def sensor():
    """La cámara manda la lectura "en vivo" del piranómetro (JSON)."""
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        abort(400, "Se espera un JSON")
    sensor_vivo["datos"] = datos
    sensor_vivo["cuando"] = time.time()
    return jsonify({"ok": True})


@app.route("/mediciones.csv")
def mediciones():
    """Todas las mediciones del piranómetro (una fila por foto)."""
    if not os.path.exists(ARCHIVO_MEDICIONES):
        abort(404, "Todavía no hay mediciones")
    resp = send_file(ARCHIVO_MEDICIONES, mimetype="text/csv")
    resp.headers["Cache-Control"] = "no-store"
    return resp


@app.route("/estado")
def estado():
    """Estado del sistema en JSON (lo usa la IHM PyQt6)."""
    return jsonify(estado_sistema(listar_fotos()))


@app.route("/lista")
def lista():
    """Lista de nombres en JSON, que usa el descargador automático."""
    return jsonify([f["nombre"] for f in listar_fotos()])


@app.route("/foto/<nombre>")
def foto(nombre):
    """Descarga una foto puntual."""
    nombre = secure_filename(nombre)
    if not os.path.exists(os.path.join(CARPETA_NUBE, nombre)):
        abort(404)
    return send_from_directory(CARPETA_NUBE, nombre, as_attachment=True)


@app.route("/descargar_todo")
def descargar_todo():
    """Arma un ZIP con todas las fotos (ordenadas en carpetas por día) y lo devuelve."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in listar_fotos():
            # Dentro del ZIP van ordenadas por día: 21082026/padron....jpg
            zf.write(os.path.join(CARPETA_NUBE, f["nombre"]),
                     os.path.join(f["dia"], f["nombre"]))
        if os.path.exists(ARCHIVO_MEDICIONES):
            zf.write(ARCHIVO_MEDICIONES, "mediciones.csv")
    buffer.seek(0)
    nombre_zip = "fotos_" + datetime.now().strftime("%d%m%Y_%H%M%S") + ".zip"
    return Response(
        buffer.getvalue(),
        mimetype="application/zip",
        headers={"Content-Disposition": f"attachment; filename={nombre_zip}"},
    )


if __name__ == "__main__":
    log.info("Servidor escuchando en el puerto %d. Carpeta nube: %s", PUERTO, CARPETA_NUBE)
    # host=0.0.0.0 para que sea accesible desde otros equipos de la red.
    app.run(host="0.0.0.0", port=PUERTO)
