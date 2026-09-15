#!/usr/bin/env bash
# Instala la IHM (interfaz gráfica PyQt6) en el Raspberry externo (Pi B).
# La deja abriéndose sola al iniciar sesión en el escritorio.
# Uso:  bash scripts/instalar_ihm.sh   (sin sudo; pide sudo cuando hace falta)
set -e

echo ">> Instalando PyQt6 y requests..."
sudo apt-get update
if ! sudo apt-get install -y python3-pyqt6 python3-requests; then
  echo ">> El paquete apt no está disponible, probando con pip..."
  pip3 install --break-system-packages PyQt6 requests
fi

DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo ">> Configurando el arranque automático en el escritorio..."
mkdir -p "$HOME/.config/autostart"
cat > "$HOME/.config/autostart/ihm-webcam.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=IHM Webcam
Comment=Panel de control de la webcam
Exec=python3 $DIR/ihm/ihm.py
Terminal=false
X-GNOME-Autostart-enabled=true
EOF

echo ""
echo ">> Listo. La IHM se abrirá sola cuando inicies sesión en el escritorio."
echo ">> Para abrirla ahora mismo:"
echo "     python3 $DIR/ihm/ihm.py"
