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
raspi-config nonint do_serial_cons 1 || true   # 1 = consola serie APAGADA
raspi-config nonint do_serial_hw 0 || true     # 0 = UART ENCENDIDA
# Respaldo por si raspi-config es viejo o no aplicó el cambio: se escribe
# directo en los archivos de arranque (Bookworm: /boot/firmware; antes: /boot).
BOOT=/boot/firmware
[ -f "$BOOT/config.txt" ] || BOOT=/boot
if ! grep -q "^enable_uart=1" "$BOOT/config.txt"; then
  sed -i '/^enable_uart=/d' "$BOOT/config.txt"
  echo "enable_uart=1" >> "$BOOT/config.txt"
fi
sed -i 's/console=serial0,[0-9]* //; s/console=ttyAMA0,[0-9]* //; s/console=ttyS0,[0-9]* //' "$BOOT/cmdline.txt"
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
