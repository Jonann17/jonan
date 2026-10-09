#!/usr/bin/env bash
# Revisa que todo esté funcionando en este Raspberry y muestra ✅ / ❌.
# No cambia nada: solo mira.
#
# Uso:  verificar          (detecta solo si es el Pi A o el Pi B)
#       verificar a | b    (para forzarlo)

DIR="$(cd "$(dirname "$(readlink -f "$0")")/.." && pwd)"
OK=0
MAL=0

bien()  { echo "  ✅ $1"; OK=$((OK + 1)); }
mal()   { echo "  ❌ $1"; [ -n "$2" ] && echo "       → $2"; MAL=$((MAL + 1)); }
aviso() { echo "  ⚠️  $1"; [ -n "$2" ] && echo "       → $2"; }

servicio() {   # servicio <nombre>
  if systemctl is-active --quiet "$1" 2>/dev/null; then
    if systemctl is-enabled --quiet "$1" 2>/dev/null; then
      bien "Servicio '$1' corriendo y con arranque automático"
    else
      mal "Servicio '$1' corre pero NO arranca solo al prender" "sudo systemctl enable $1"
    fi
  else
    mal "Servicio '$1' NO está corriendo" "ver el error: journalctl -u $1 -n 20 --no-pager"
  fi
}

errores_recientes() {   # errores_recientes <servicio>
  local n
  n="$(journalctl -u "$1" --since "-10 min" -p err --no-pager -q 2>/dev/null | wc -l)"
  if [ "$n" -gt 0 ]; then
    aviso "'$1' registró $n error(es) en los últimos 10 min" "journalctl -u $1 -n 30 --no-pager"
  fi
}

# Lee un campo del JSON de /estado (sin depender de jq)
campo() {
  python3 -c "import json,sys; d=json.load(sys.stdin); v=d.get('$1'); print('' if v is None else v)" \
    <<<"$ESTADO" 2>/dev/null
}

ROL="$(echo "${1:-}" | tr 'AB' 'ab')"
if [ -z "$ROL" ]; then
  if nmcli -t -f NAME connection show 2>/dev/null | grep -qx "hotspot-fotos"; then
    ROL=a
  else
    ROL=b
  fi
fi

echo ""
echo "── Versión ──"
if [ -d "$DIR/../.git" ]; then
  echo "  Rama:   $(git -C "$DIR" branch --show-current)"
  echo "  Commit: $(git -C "$DIR" log -1 --format='%h %s (%cr)')"
fi

# ════════════════════════════════════════════════════════════════════════
if [ "$ROL" = a ]; then
  echo ""
  echo "════ Pi A: cámara + servidor + hotspot ════"

  echo ""
  echo "── Red WiFi (hotspot FotosPi) ──"
  if nmcli -t -f NAME connection show --active 2>/dev/null | grep -qx "hotspot-fotos"; then
    bien "Hotspot 'FotosPi' encendido"
  else
    mal "Hotspot apagado" "sudo nmcli connection up hotspot-fotos"
  fi
  if ip -4 addr show 2>/dev/null | grep -q "192.168.50.1/"; then
    bien "IP del hotspot 192.168.50.1"
  else
    mal "No tiene la IP 192.168.50.1" "sudo nmcli connection down hotspot-fotos; sudo nmcli connection up hotspot-fotos"
  fi

  echo ""
  echo "── Servicios ──"
  servicio servidor
  servicio camara
  errores_recientes servidor
  errores_recientes camara

  echo ""
  echo "── Servidor web ──"
  ESTADO="$(curl -s --max-time 5 http://127.0.0.1:8000/estado)"
  if [ -n "$ESTADO" ]; then
    bien "Responde en http://192.168.50.1:8000"
    echo "       Fotos guardadas: $(campo total_fotos) · intervalo: $(campo intervalo_camara) s"
    if [ "$(campo camara_viva)" = "True" ]; then
      bien "La cámara se comunica con el servidor"
    else
      mal "La cámara no se comunica con el servidor" "journalctl -u camara -n 30 --no-pager"
    fi
    if [ "$(campo capturando)" = "True" ]; then
      echo "       Estado: CAPTURANDO · última foto: $(campo camara_txt)"
    else
      echo "       Estado: EN ESPERA (normal tras reiniciar; se inicia desde la IHM)"
    fi
    if [ "$(campo hora_ajustada)" = "True" ]; then
      bien "Hora ajustada: $(campo hora_pi_txt)"
    else
      aviso "Hora sin ajustar desde que prendió ($(campo hora_pi_txt))" "ajustala desde la IHM, pestaña Control"
    fi
  else
    mal "El servidor no responde" "journalctl -u servidor -n 30 --no-pager"
  fi

  echo ""
  echo "── Webcam ──"
  if [ -e /dev/video0 ]; then
    bien "Webcam conectada (/dev/video0)"
  else
    mal "No se ve la webcam" "revisá el cable USB y corré: ls /dev/video*"
  fi
  if command -v fswebcam >/dev/null; then
    bien "fswebcam instalado"
  else
    mal "Falta fswebcam" "actualizar"
  fi

  echo ""
  echo "── Arduino / piranómetro ──"
  PUERTO="$(cd "$DIR" && python3 -c 'from comun import cargar_config, puerto_arduino; c = cargar_config(); print(puerto_arduino(c.get("arduino", "puerto", fallback="auto")))' 2>/dev/null)"
  case "$PUERTO" in
    /dev/ttyACM*|/dev/ttyUSB*|/dev/serial/by-id/*)
      bien "Arduino conectado por cable USB ($PUERTO)"
      PISTA="revisá el cable USB entre el Arduino y el Pi"
      ;;
    *)
      PISTA="revisá cables (pin 8/9, GND, 5V) y el conversor de nivel, o conectá el Arduino por USB"
      if [ -e /dev/serial0 ]; then
        bien "UART habilitada (/dev/serial0)"
      else
        mal "No hay Arduino por USB y la UART está apagada (no existe /dev/serial0)" \
            "conectá el Arduino por cable USB, o: actualizar (y después reiniciar)"
      fi
      if grep -q "console=serial0" /boot/firmware/cmdline.txt /boot/cmdline.txt 2>/dev/null; then
        mal "La consola de Linux sigue usando el puerto serie" "actualizar   (y después reiniciar)"
      fi
      ;;
  esac
  USUARIO="$(sed -n 's/^User=//p' /etc/systemd/system/camara.service 2>/dev/null)"
  if id -nG "${USUARIO:-$(whoami)}" 2>/dev/null | grep -qw dialout; then
    bien "Usuario '${USUARIO:-$(whoami)}' con permiso para el puerto serie"
  else
    mal "Usuario sin permiso para el puerto serie (grupo dialout)" "actualizar   (y después reiniciar)"
  fi
  if [ -n "$ESTADO" ]; then
    SENSOR="$(python3 -c "import json,sys; s=json.load(sys.stdin).get('sensor'); print(f\"{s.get('v_now')} V · {s.get('g_now')} W/m² · sat={s.get('sat')}\" if s else '')" <<<"$ESTADO" 2>/dev/null)"
    if [ -n "$SENSOR" ]; then
      bien "El Arduino responde: $SENSOR"
    else
      mal "No llegan datos del Arduino" "$PISTA"
    fi
  fi

  echo ""
  echo "── Permisos y espacio ──"
  if [ -f /etc/sudoers.d/webcam-hora ]; then
    bien "Permiso para ajustar la hora desde la IHM"
  else
    mal "Falta el permiso para ajustar la hora" "actualizar"
  fi

# ════════════════════════════════════════════════════════════════════════
else
  echo ""
  echo "════ Pi B: descargador + IHM ════"

  echo ""
  echo "── Red WiFi ──"
  RED="$(nmcli -t -f NAME,DEVICE connection show --active 2>/dev/null | grep -v ':lo$' | cut -d: -f1 | paste -sd, -)"
  echo "       Conectado a: ${RED:-ninguna red}"
  if ping -c 2 -W 2 192.168.50.1 >/dev/null 2>&1; then
    bien "Llega al Pi A (192.168.50.1)"
  else
    mal "No llega al Pi A" "sudo nmcli connection up FotosPi"
  fi

  echo ""
  echo "── Servicios ──"
  servicio descargador
  errores_recientes descargador

  echo ""
  echo "── Servidor del Pi A ──"
  ESTADO="$(curl -s --max-time 5 http://192.168.50.1:8000/estado)"
  if [ -n "$ESTADO" ]; then
    bien "El servidor responde · fotos en la nube: $(campo total_fotos)"
    if [ "$(campo desc_ok)" = "True" ]; then
      bien "El servidor ve al descargador ($(campo desc_txt))"
    else
      aviso "El servidor todavía no recibió el latido del descargador" "esperá unos minutos"
    fi
  else
    mal "El servidor del Pi A no responde"
  fi

  echo ""
  echo "── Fotos descargadas ──"
  CARPETA="$(sed -n '/^\[descargador\]/,/^\[/ s/^carpeta_local *= *//p' "$DIR/config.ini" | head -1)"
  if [ -d "$CARPETA" ]; then
    bien "$(find "$CARPETA" -name '*.jpg' | wc -l) fotos en $CARPETA"
  else
    mal "No existe la carpeta $CARPETA" "revisá carpeta_local en config.ini"
  fi

  echo ""
  echo "── IHM ──"
  if python3 -c "import PyQt6.QtWidgets" 2>/dev/null; then
    bien "PyQt6 instalado"
  else
    mal "Falta PyQt6" "actualizar"
  fi
  if python3 -c "import matplotlib" 2>/dev/null; then
    bien "matplotlib instalado (pestaña Gráfico)"
  else
    mal "Falta matplotlib" "actualizar"
  fi
  if [ -f "$HOME/.config/autostart/ihm-webcam.desktop" ]; then
    bien "La IHM se abre sola al iniciar el escritorio"
  else
    mal "La IHM no está en el inicio automático" "actualizar"
  fi
  if pgrep -f "ihm/ihm.py" >/dev/null; then
    bien "La IHM está abierta ahora"
  else
    aviso "La IHM no está abierta" "python3 $DIR/ihm/ihm.py &"
  fi
fi

# ── Común a los dos ──
LIBRE="$(df -h "$HOME" | awk 'NR==2 {print $4}')"
USO="$(df "$HOME" | awk 'NR==2 {gsub("%",""); print $5}')"
if [ "${USO:-0}" -lt 90 ]; then
  bien "Espacio en disco: $LIBRE libres"
else
  mal "Disco casi lleno: quedan $LIBRE" "borrá fotos viejas o usá una tarjeta más grande"
fi

echo ""
echo "════════════════════════════════════════"
if [ "$MAL" -eq 0 ]; then
  echo " ✅ Todo correcto ($OK chequeos OK)"
else
  echo " ❌ $MAL problema(s), $OK chequeos OK — mirá las flechas →"
fi
echo "════════════════════════════════════════"
