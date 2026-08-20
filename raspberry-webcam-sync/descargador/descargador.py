#!/usr/bin/env python3
"""
descargador.py  —  Se ejecuta en el SEGUNDO Raspberry Pi.

Qué hace:
  1. Cada cierto tiempo se conecta al servidor y pide la lista de fotos.
  2. Descarga a su carpeta local todas las fotos que todavía no tenga.
  3. No vuelve a descargar las que ya bajó (compara por nombre).
  4. "Self-check": si el Pi se apaga y se prende, systemd lo vuelve a lanzar
     solo y sigue descargando lo que falte (las que ya están no se repiten).

Requisitos en el Pi:
    sudo apt install python3-requests
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from comun import cargar_config, configurar_logging, asegurar_carpeta

import requests

log = configurar_logging("descargador")


def obtener_lista(url_servidor):
    """Pide al servidor la lista de nombres de fotos."""
    url = url_servidor.rstrip("/") + "/lista"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.json()


def descargar(url_servidor, nombre, carpeta):
    """Descarga una foto puntual a la carpeta local."""
    url = url_servidor.rstrip("/") + "/foto/" + nombre
    destino = os.path.join(carpeta, nombre)
    temporal = destino + ".parcial"
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        with open(temporal, "wb") as f:
            for bloque in r.iter_content(chunk_size=8192):
                f.write(bloque)
    # Renombrar al final evita quedarnos con archivos a medias si se corta.
    os.replace(temporal, destino)
    log.info("Descargada: %s", nombre)


def sincronizar(url_servidor, carpeta):
    """Descarga todas las fotos que falten. Devuelve cuántas bajó."""
    try:
        remotas = obtener_lista(url_servidor)
    except requests.RequestException as e:
        log.warning("No se pudo conectar al servidor: %s", e)
        return 0

    locales = set(os.listdir(carpeta))
    nuevas = 0
    for nombre in remotas:
        if nombre in locales:
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
        if nuevas:
            log.info("Se descargaron %d fotos nuevas.", nuevas)
        else:
            log.info("Sin fotos nuevas. Esperando %d segundos...", intervalo)
        time.sleep(intervalo)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log.info("Descargador detenido por el usuario.")
