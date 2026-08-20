#!/usr/bin/env bash
# ============================================================
#  configurar_hotspot.sh
#  Convierte al Raspberry del SERVIDOR en su propio hotspot WiFi
#  (Access Point). El otro dispositivo se conecta a esta red y
#  descarga las fotos, SIN necesidad de un router.
#
#  Usa NetworkManager (nmcli), que es lo estándar en Raspberry Pi
#  OS actual (Bookworm). El hotspot arranca solo al prender el Pi.
#
#  Uso:
#     sudo bash scripts/configurar_hotspot.sh
#  o con valores propios:
#     sudo SSID="FotosPi" PASSWORD="miclave123" IP_AP="192.168.50.1" \
#          bash scripts/configurar_hotspot.sh
# ============================================================
set -e

# --- Datos del hotspot (podés cambiarlos con variables de entorno) ---
SSID="${SSID:-FotosPi}"            # Nombre de la red WiFi que crea el Pi
PASSWORD="${PASSWORD:-fotospi1234}"  # Contraseña (mínimo 8 caracteres)
IP_AP="${IP_AP:-192.168.50.1}"    # IP fija del Pi servidor en su red
INTERFAZ="${INTERFAZ:-wlan0}"     # WiFi interna del Pi 3 B
CONEXION="hotspot-fotos"

if [ "${#PASSWORD}" -lt 8 ]; then
  echo "ERROR: la contraseña debe tener al menos 8 caracteres." >&2
  exit 1
fi

if ! command -v nmcli >/dev/null 2>&1; then
  echo "ERROR: no se encontró 'nmcli' (NetworkManager)." >&2
  echo "En Raspberry Pi OS Bookworm ya viene. Si usás una versión vieja," >&2
  echo "instalá NetworkManager:  sudo apt install network-manager" >&2
  exit 1
fi

echo ">> Creando el hotspot '$SSID' en $INTERFAZ con IP $IP_AP ..."

# Si ya existía una conexión con este nombre, la borramos para recrearla limpia.
nmcli connection delete "$CONEXION" >/dev/null 2>&1 || true

# Crear la conexión en modo Access Point.
nmcli connection add type wifi ifname "$INTERFAZ" con-name "$CONEXION" \
      autoconnect yes ssid "$SSID"

# Modo AP + banda 2.4 GHz (la más compatible en el Pi 3 B).
nmcli connection modify "$CONEXION" \
      802-11-wireless.mode ap \
      802-11-wireless.band bg \
      ipv4.method shared \
      ipv4.addresses "${IP_AP}/24"

# Seguridad WPA2 con contraseña.
nmcli connection modify "$CONEXION" \
      wifi-sec.key-mgmt wpa-psk \
      wifi-sec.psk "$PASSWORD"

# Levantar el hotspot ahora.
nmcli connection up "$CONEXION"

echo ""
echo ">> ¡Hotspot activo! Se levanta solo cada vez que prendés el Pi."
echo "   Red WiFi:      $SSID"
echo "   Contraseña:    $PASSWORD"
echo "   IP del server: $IP_AP"
echo ""
echo ">> IMPORTANTE: en config.ini, poné el servidor apuntando a esta IP:"
echo "     [servidor]     -> corre en este Pi (puerto 8000)"
echo "     url_servidor = http://$IP_AP:8000   (en [camara] y [descargador])"
echo ""
echo ">> En el OTRO dispositivo: conectate a la red WiFi '$SSID' y entrá a"
echo "     http://$IP_AP:8000"
echo ""
echo ">> NOTA: al usar $INTERFAZ como hotspot, este Pi ya no se conecta a otra"
echo "   red WiFi por esa placa. Si además necesitás internet en el servidor,"
echo "   conectalo por cable de red (Ethernet)."
echo ""
echo ">> Para desactivar el hotspot:  sudo nmcli connection down $CONEXION"
echo "   Para borrarlo:               sudo nmcli connection delete $CONEXION"
