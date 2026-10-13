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

# --- Permiso para AJUSTAR LA HORA desde la IHM ---
# El servidor corre con el usuario del .service (User=...). Le damos permiso
# para usar SOLO 'date' y 'fake-hwclock' con sudo, sin contraseña.
USUARIO="$(sed -n 's/^User=//p' "$DIR/systemd/servidor.service")"
USUARIO="${USUARIO:-pi}"
echo ">> Permitiendo que '$USUARIO' ajuste la hora (sudoers)..."
apt-get install -y fake-hwclock
REGLA=/etc/sudoers.d/webcam-hora
echo "$USUARIO ALL=(root) NOPASSWD: $(command -v date), $(command -v fake-hwclock)" > "$REGLA"
chmod 440 "$REGLA"
visudo -cf "$REGLA"
# Sin internet, la sincronización automática (NTP) no sirve y puede pisar
# la hora que mandamos desde la IHM al reconectarse.
timedatectl set-ntp false || true

echo ">> Activando el arranque automático al prender..."
systemctl daemon-reload
systemctl enable servidor.service
systemctl restart servidor.service

echo ">> Listo. El servidor arranca solo al prender."
echo ">> Estado:  systemctl status servidor.service"
echo ">> Logs:    journalctl -u servidor.service -f"
