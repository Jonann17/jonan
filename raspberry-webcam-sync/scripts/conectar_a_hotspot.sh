#!/usr/bin/env bash
# ============================================================
#  conectar_a_hotspot.sh
#  Conecta un Raspberry (el de la CÁMARA o el DESCARGADOR) a la
#  red WiFi que crea el Pi servidor. Queda guardada y se reconecta
#  sola al prender.
#
#  Uso:
#     sudo bash scripts/conectar_a_hotspot.sh
#  o con valores propios:
#     sudo SSID="FotosPi" PASSWORD="miclave123" \
#          bash scripts/conectar_a_hotspot.sh
# ============================================================
set -e

SSID="${SSID:-FotosPi}"
PASSWORD="${PASSWORD:-fotospi1234}"
INTERFAZ="${INTERFAZ:-wlan0}"

if ! command -v nmcli >/dev/null 2>&1; then
  echo "ERROR: no se encontró 'nmcli' (NetworkManager)." >&2
  exit 1
fi

echo ">> Conectando a la red WiFi '$SSID' ..."
nmcli device wifi connect "$SSID" password "$PASSWORD" ifname "$INTERFAZ"

# Que se reconecte automáticamente al prender.
nmcli connection modify "$SSID" connection.autoconnect yes 2>/dev/null || true

echo ""
echo ">> Conectado. Este Pi ya forma parte de la red del servidor."
echo ">> Verificá que llega al servidor (cambiá la IP si la modificaste):"
echo "     ping -c 3 192.168.50.1"
