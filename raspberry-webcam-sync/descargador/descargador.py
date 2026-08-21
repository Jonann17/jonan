#!/usr/bin/env python3
"""
descargador.py  —  Se ejecuta en el SEGUNDO Raspberry Pi.

Qué hace:
  1. Cada cierto tiempo se conecta al servidor y pide la lista de fotos.
  2. Descarga a su carpeta local todas las fotos que todavía no tenga,
     ORDENADAS POR DÍA: cada foto va a una subcarpeta con la fecha del
     nombre (DDMMAAAA). Ejemplo:
         fotos_descargadas/21082026/padron0001_21082026_143000.jpg
     Así nunca se mezclan las fotos nuevas con las viejas.
  3. No vuelve a descargar las que ya bajó (compara por nombre, en
     cualquier subcarpeta).
  4. Le avisa al servidor que está vivo (un "latido"), para que la página
     web muestre en verde que el descargador está funcionando.
  5. "Self-check": si el Pi se apaga y se prende, systemd lo vuelve a lanzar
     solo y sigue descargando lo que falte.

Requisitos en el Pi:
    sudo apt install python3-requests
"""

import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from comun import cargar_config, configurar_logging, asegurar_carpeta

import requests

log = configurar_logging("descargador")

# Detecta la fecha DDMMAAAA (8 dígitos) dentro del nombre de la foto.
RE_FECHA = re.compile(r"_(\d{8})_")


def fecha_de_nombre(nombre):
    """Devuelve la carpeta-día (DDMMAAAA) sacada del nombre, o 'sin_fecha'."""
    m = RE_FECHA.search(nombre)
    return m.group(1) if m else "sin_fecha"


def fotos_ya_bajadas(carpeta):
    """Nombres de todas las fotos que ya tenemos, mirando todas las subcarpetas."""
    tengo = set()
    for raiz, _dirs, archivos in os.walk(carpeta):
        for a in archivos:
            if a.lower().endswith(".jpg"):
                tengo.add(a)
    return tengo


def obtener_lista(url_servidor):
    """Pide al servidor la lista de nombres de fotos."""
    url = url_servidor.rstrip("/") + "/lista"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.json()


def descargar(url_servidor, nombre, carpeta):
    """Descarga una foto a la subcarpeta del día que le corresponde."""
    url = url_servidor.rstrip("/") + "/foto/" + nombre
    subcarpeta = asegurar_carpeta(os.path.join(carpeta, fecha_de_nombre(nombre)))
    destino = os.path.join(subcarpeta, nombre)
    temporal = destino + ".parcial"
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        with open(temporal, "wb") as f:
            for bloque in r.iter_content(chunk_size=8192):
                f.write(bloque)
    # Renombrar al final evita quedarnos con archivos a medias si se corta.
    os.replace(temporal, destino)
    log.info("Descargada: %s/%s", fecha_de_nombre(nombre), nombre)


def enviar_latido(url_servidor):
    """Le avisa al servidor que el descargador está vivo (para el panel web)."""
    url = url_servidor.rstrip("/") + "/latido"
    try:
        requests.post(url, data={"origen": "descargador"}, timeout=10)
    except requests.RequestException:
        pass  # si el servidor no responde, no pasa nada, se reintenta luego


def sincronizar(url_servidor, carpeta):
    """Descarga todas las fotos que falten. Devuelve cuántas bajó."""
    try:
        remotas = obtener_lista(url_servidor)
    except requests.RequestException as e:
        log.warning("No se pudo conectar al servidor: %s", e)
        return 0

    tengo = fotos_ya_bajadas(carpeta)
    nuevas = 0
    for nombre in remotas:
        if nombre in tengo:
            continue
        try:
            descargar(url_servidor, nombre, carpeta)
            nuevas += 1
        except requests.RequestException as e:
            log.warning("Error al descargar %s: %s", nombre, e)
    return nuevas


def main():
    config = cargar_config()
    url_servidor = config["descargador"]["url_servidor"]
    intervalo = config.getint("descargador", "intervalo_segundos")
    carpeta = asegurar_carpeta(config["descargador"]["carpeta_local"])

    log.info("Descargador iniciado. Servidor=%s  Intervalo=%ss  Carpeta=%s",
             url_servidor, intervalo, carpeta)

    while True:
        nuevas = sincronizar(url_servidor, carpeta)
        enviar_latido(url_servidor)
        if nuevas:
            log.info("Se descargaron %d fotos nuevas (ordenadas por día).", nuevas)
        else:
            log.info("Sin fotos nuevas. Esperando %d segundos...", intervalo)
        time.sleep(intervalo)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log.info("Descargador detenido por el usuario.")
