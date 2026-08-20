#!/usr/bin/env bash
# Instala el SERVIDOR web (la nube) en el equipo elegido.
# Uso:  sudo bash scripts/instalar_servidor.sh
set -e

echo ">> Instalando dependencias (Flask)..."
apt-get update
apt-get install -y python3-flask

echo ">> Copiando el servicio a systemd..."
DIR="$(cd "$(dirname "$0")/.." && pwd)"
cp "$DIR/systemd/servidor.service" /etc/systemd/system/servidor.service

echo ">> Activando el arranque automático al prender..."
systemctl daemon-reload
systemctl enable servidor.service
systemctl restart servidor.service

echo ">> Listo. El servidor arranca solo al prender."
echo ">> Estado:  systemctl status servidor.service"
echo ">> Logs:    journalctl -u servidor.service -f"
