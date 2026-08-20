"""
comun.py
Funciones compartidas por la cámara, el servidor y el descargador.
"""

import configparser
import logging
import os

# Ruta del config.ini (está en la misma carpeta que este archivo)
RUTA_CONFIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini")


def cargar_config():
    """Lee config.ini y devuelve el objeto de configuración."""
    config = configparser.ConfigParser()
    leidos = config.read(RUTA_CONFIG, encoding="utf-8")
    if not leidos:
        raise FileNotFoundError(f"No se encontró el archivo de configuración: {RUTA_CONFIG}")
    return config


def configurar_logging(nombre):
    """Configura logging a consola (systemd lo captura en journalctl)."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return logging.getLogger(nombre)


def asegurar_carpeta(ruta):
    """Crea la carpeta si no existe (no falla si ya existe)."""
    os.makedirs(ruta, exist_ok=True)
    return ruta
