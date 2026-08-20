#!/usr/bin/env bash
# Instala el DESCARGADOR en el segundo Raspberry Pi.
# Uso:  sudo bash scripts/instalar_descargador.sh
set -e

echo ">> Instalando dependencias (requests)..."
apt-get update
apt-get install -y python3-requests

echo ">> Copiando el servicio a systemd..."
DIR="$(cd "$(dirname "$0")/.." && pwd)"
cp "$DIR/systemd/descargador.service" /etc/systemd/system/descargador.service

echo ">> Activando el arranque automático al prender el Raspberry..."
systemctl daemon-reload
systemctl enable descargador.service
systemctl restart descargador.service

echo ">> Listo. El descargador trabaja solo y arranca al prender el Pi."
echo ">> Estado:  systemctl status descargador.service"
echo ">> Logs:    journalctl -u descargador.service -f"
