#!/usr/bin/env bash
# Instala el servicio de la CÁMARA en el Raspberry Pi de la webcam.
# Uso:  sudo bash scripts/instalar_camara.sh
set -e

echo ">> Instalando dependencias (fswebcam, requests y pyserial)..."
apt-get update
apt-get install -y fswebcam python3-requests python3-serial

# --- Puerto serie de los GPIO 14/15 para el Arduino (piranómetro) ---
# Se habilita la UART y se desactiva la consola de Linux por ese puerto
# (si no, Linux "le habla" al Arduino y ensucia las mediciones).
echo ">> Habilitando la UART (GPIO 14/15) para el Arduino..."
raspi-config nonint do_serial_cons 1   # 1 = consola serie APAGADA
raspi-config nonint do_serial_hw 0     # 0 = UART ENCENDIDA
DIR_TMP="$(cd "$(dirname "$0")/.." && pwd)"
USUARIO="$(sed -n 's/^User=//p' "$DIR_TMP/systemd/camara.service")"
usermod -aG dialout,video "${USUARIO:-pi}"
echo ">> (La UART queda activa después de reiniciar el Pi: sudo reboot)"

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
