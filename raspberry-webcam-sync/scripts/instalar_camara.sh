#!/usr/bin/env bash
# Instala el servicio de la CÁMARA en el Raspberry Pi de la webcam.
# Uso:  sudo bash scripts/instalar_camara.sh
set -e

echo ">> Instalando dependencias (fswebcam y requests)..."
apt-get update
apt-get install -y fswebcam python3-requests

echo ">> Copiando el servicio a systemd..."
DIR="$(cd "$(dirname "$0")/.." && pwd)"
cp "$DIR/systemd/camara.service" /etc/systemd/system/camara.service

echo ">> Activando el arranque automático al prender el Raspberry..."
systemctl daemon-reload
systemctl enable camara.service
systemctl restart camara.service

echo ">> Listo. La cámara ya trabaja sola y arranca al prender el Pi."
echo ">> Ver el estado:   systemctl status camara.service"
echo ">> Ver los logs:    journalctl -u camara.service -f"
