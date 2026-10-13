#!/usr/bin/env bash
# ============================================================
#  conectar_a_hotspot.sh
#  Conecta un Raspberry (el de la CÁMARA o el DESCARGADOR) a la
#  red WiFi que crea el Pi servidor. Queda guardada y se reconecta
#  sola al prender.
#
#  Uso (red con contraseña):
#     sudo bash scripts/conectar_a_hotspot.sh
#  o con valores propios:
#     sudo SSID="FotosPi" PASSWORD="miclave123" COUNTRY="PY" \
#          bash scripts/conectar_a_hotspot.sh
#
#  Si el hotspot es una red ABIERTA (sin contraseña):
#     sudo ABIERTO=1 bash scripts/conectar_a_hotspot.sh
# ============================================================
set -e

SSID="${SSID:-FotosPi}"
PASSWORD="${PASSWORD:-fotospi1234}"
INTERFAZ="${INTERFAZ:-wlan0}"
COUNTRY="${COUNTRY:-PY}"
ABIERTO="${ABIERTO:-0}"

if ! command -v nmcli >/dev/null 2>&1; then
  echo "ERROR: no se encontró 'nmcli' (NetworkManager)." >&2
  exit 1
fi

# Fijar el país del WiFi (evita problemas de canal/regulatorios).
if command -v raspi-config >/dev/null 2>&1; then
  raspi-config nonint do_wifi_country "$COUNTRY" || true
fi
iw reg set "$COUNTRY" 2>/dev/null || true

# Borrar cualquier perfil viejo de esta red que haya quedado a medias.
# (Si no, NetworkManager reintenta con datos guardados y da el error
#  "Segredos foram requisitados, mas não fornecidos" / "no secrets".)
nmcli connection delete "$SSID" >/dev/null 2>&1 || true
nmcli device wifi rescan >/dev/null 2>&1 || true

echo ">> Conectando a la red WiFi '$SSID' ..."
if [ "$ABIERTO" = "1" ]; then
  nmcli device wifi connect "$SSID" ifname "$INTERFAZ"
else
  nmcli device wifi connect "$SSID" password "$PASSWORD" ifname "$INTERFAZ"
fi

# Que se reconecte automáticamente al prender.
nmcli connection modify "$SSID" connection.autoconnect yes 2>/dev/null || true

echo ""
echo ">> Conectado. Este Pi ya forma parte de la red del servidor."
echo ">> Verificá que llega al servidor (cambiá la IP si la modificaste):"
echo "     ping -c 3 192.168.50.1"
