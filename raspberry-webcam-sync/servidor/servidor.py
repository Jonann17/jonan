#!/usr/bin/env python3
"""
servidor.py  —  La "nube". Puede correr en cualquiera de los dos Raspberry,
en una PC de la red, o en el mismo Pi del descargador.

Qué hace:
  - Recibe las fotos que sube el Pi de la cámara (endpoint /subir).
  - Guarda TODAS las fotos en carpeta_nube.
  - Muestra una página web con la lista de fotos y botones para descargar.
  - Deja descargar una foto (/foto/<nombre>), todas en un ZIP (/descargar_todo),
    y una lista en JSON (/lista) que usa el descargador automático.

Requisitos en el equipo servidor:
    sudo apt install python3-flask
    # o:  pip3 install flask

Cómo probar desde un navegador:
    http://IP_DEL_SERVIDOR:8000
"""

import io
import os
import sys
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

app = Flask(__name__)

PAGINA = """
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Nube de fotos - Webcam Raspberry Pi</title>
  <style>
    body { font-family: system-ui, sans-serif; margin: 2rem; background:#0f1115; color:#e6e6e6; }
    h1 { font-size: 1.4rem; }
    a { color:#6cb6ff; }
    .barra { margin: 1rem 0; }
    .btn { display:inline-block; background:#2563eb; color:#fff; padding:.5rem .9rem;
           border-radius:8px; text-decoration:none; }
    table { border-collapse: collapse; width:100%; max-width:700px; }
    th, td { text-align:left; padding:.4rem .6rem; border-bottom:1px solid #2a2f3a; }
    .vacio { color:#9aa4b2; }
  </style>
</head>
<body>
  <h1>📷 Nube de fotos de la webcam</h1>
  <p>Total de fotos: <strong>{{ fotos|length }}</strong></p>
  <div class="barra">
    {% if fotos %}<a class="btn" href="/descargar_todo">⬇ Descargar todas (ZIP)</a>{% endif %}
  </div>
  {% if fotos %}
  <table>
    <tr><th>Foto</th><th>Tamaño</th><th>Descargar</th></tr>
    {% for f in fotos %}
    <tr>
      <td>{{ f.nombre }}</td>
      <td>{{ f.kb }} KB</td>
      <td><a href="/foto/{{ f.nombre }}">⬇</a></td>
    </tr>
    {% endfor %}
  </table>
  {% else %}
  <p class="vacio">Todavía no hay fotos. Esperando a que la cámara suba la primera...</p>
  {% endif %}
</body>
</html>
"""


def listar_fotos():
    fotos = []
    for nombre in sorted(os.listdir(CARPETA_NUBE)):
        if nombre.lower().endswith(".jpg"):
            ruta = os.path.join(CARPETA_NUBE, nombre)
            fotos.append({
                "nombre": nombre,
                "kb": round(os.path.getsize(ruta) / 1024, 1),
            })
    return fotos


@app.route("/")
def inicio():
    return render_template_string(PAGINA, fotos=listar_fotos())


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
    log.info("Foto recibida: %s (%d bytes)", nombre, os.path.getsize(destino))
    return jsonify({"ok": True, "nombre": nombre})


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
    """Arma un ZIP con todas las fotos y lo devuelve."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in listar_fotos():
            zf.write(os.path.join(CARPETA_NUBE, f["nombre"]), f["nombre"])
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
