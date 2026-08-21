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

Requisitos en el equipo servidor:
    sudo apt install python3-flask

Cómo probar desde un navegador:
    http://IP_DEL_SERVIDOR:8000
"""

import io
import os
import re
import sys
import time
import zipfile
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from comun import cargar_config, configurar_logging, asegurar_carpeta

from flask import (
    Flask, request, send_from_directory, jsonify,
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

app = Flask(__name__)

# Guarda cuándo fue el último "latido" de cada componente (en memoria).
ultimo_latido = {}

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

    # Cámara: en base a la foto más nueva.
    if fotos:
        edad_foto = ahora - max(f["mtime"] for f in fotos)
    else:
        edad_foto = None
    camara_ok = edad_foto is not None and edad_foto < INTERVALO_CAMARA * 2 + 60

    # Descargador: en base a su último latido.
    lat = ultimo_latido.get("descargador")
    edad_lat = (ahora - lat) if lat else None
    desc_ok = edad_lat is not None and edad_lat < INTERVALO_DESCARGA * 2 + 60

    return {
        "servidor_ok": True,  # si estás viendo la página, el servidor anda
        "camara_ok": camara_ok,
        "camara_txt": hace_cuanto(edad_foto) if edad_foto is not None else "sin fotos aún",
        "desc_ok": desc_ok,
        "desc_txt": hace_cuanto(edad_lat) if edad_lat is not None else "sin conexión aún",
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
      <div class="titulo">Total fotos</div>
      <div class="valor">🖼️ {{ fotos|length }}</div>
    </div>
  </div>

  <div class="barra">
    {% if fotos %}<a class="btn" href="/descargar_todo">⬇ Descargar todas (ZIP)</a>{% endif %}
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


@app.route("/")
def inicio():
    fotos = listar_fotos()
    return render_template_string(
        PAGINA, fotos=fotos, e=estado_sistema(fotos), grupos=agrupar_por_dia(fotos)
    )


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
    log.info("Foto recibida: %s (%d bytes)", nombre, os.path.getsize(destino))
    return jsonify({"ok": True, "nombre": nombre})


@app.route("/latido", methods=["POST"])
def latido():
    """Un componente (ej. el descargador) avisa que está vivo."""
    origen = request.form.get("origen", "desconocido")
    ultimo_latido[origen] = time.time()
    return jsonify({"ok": True})


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
