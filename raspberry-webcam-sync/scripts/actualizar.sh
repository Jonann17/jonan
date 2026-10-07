#!/usr/bin/env bash
# Actualiza este Raspberry a la última versión del proyecto, en un solo paso.
#
#   - Baja la última versión de GitHub (rama RAMA de abajo).
#   - Vuelve a ajustar rutas y usuario (estos Pi no usan el usuario "pi").
#   - Conserva el padrón que tenías en config.ini.
#   - Reinstala lo que corresponde a ESTE Pi y lo reinicia.
#
# Detecta solo qué Pi es: si tiene el hotspot "hotspot-fotos" es el Pi A
# (cámara + servidor); si no, es el Pi B (descargador + IHM). Se puede
# forzar con:  actualizar a   ·   actualizar b
#
# Primera vez (todavía no existe el comando):
#   curl -sL https://raw.githubusercontent.com/Jonann17/jonan/claude/trusting-lamport-hd05q6/raspberry-webcam-sync/scripts/actualizar.sh | bash
# Las siguientes veces alcanza con escribir:
#   actualizar
#
# Correrlo como usuario normal (SIN sudo): pide la contraseña cuando hace falta.

# Todo va dentro de main() para que bash lea el script entero antes de
# empezar: el "git checkout" de abajo puede reemplazar este mismo archivo.
main() {
  set -e
  RAMA="claude/trusting-lamport-hd05q6"
  REPO_URL="https://github.com/Jonann17/jonan.git"
  RAIZ="$HOME/jonan"
  DIR="$RAIZ/raspberry-webcam-sync"

  if [ "$(id -u)" -eq 0 ]; then
    echo "!! Correlo SIN sudo:  actualizar"
    exit 1
  fi

  # ── ¿Qué Pi es? ──
  ROL="$(echo "${1:-}" | tr 'AB' 'ab')"
  if [ -z "$ROL" ]; then
    if nmcli -t -f NAME connection show 2>/dev/null | grep -qx "hotspot-fotos"; then
      ROL=a
    else
      ROL=b
    fi
  fi
  if [ "$ROL" = a ]; then
    echo "== Pi A (cámara + servidor) =="
  elif [ "$ROL" = b ]; then
    echo "== Pi B (descargador + IHM) =="
  else
    echo "!! Uso: actualizar [a|b]"
    exit 1
  fi

  # ── Bajar la última versión ──
  if [ ! -d "$RAIZ/.git" ]; then
    echo ">> Clonando el proyecto en $RAIZ ..."
    git clone -b "$RAMA" "$REPO_URL" "$RAIZ"
  fi
  cd "$DIR"

  # Si venimos de la re-ejecución (ver abajo), el padrón ya viene guardado.
  if [ -z "${ACTUALIZAR_NUEVO:-}" ]; then
    PADRON="$(sed -n 's/^padron *= *//p' config.ini 2>/dev/null | head -1)"
    cp config.ini "$HOME/config.ini.respaldo" 2>/dev/null || true
  else
    PADRON="${ACTUALIZAR_PADRON:-}"
  fi

  echo ">> Bajando la última versión de GitHub..."
  if ! git fetch origin "$RAMA"; then
    echo ""
    echo "!! No se pudo conectar a GitHub. Este Pi necesita INTERNET."
    echo "   (El Pi B, conectado solo a FotosPi, no tiene: enchufale un cable"
    echo "    Ethernet y volvé a correr: actualizar)"
    exit 1
  fi
  # Los cambios locales (rutas ajustadas a mano) se descartan y se vuelven
  # a aplicar abajo; config.ini quedó respaldado en ~/config.ini.respaldo.
  git reset -q --hard
  git checkout -q -B "$RAMA" "origin/$RAMA"

  # Lo que está corriendo es la versión VIEJA de este script (bash ya la
  # tenía cargada). Se vuelve a arrancar con la versión recién bajada, así
  # cualquier paso nuevo (por ejemplo, un comando nuevo) se aplica ya.
  if [ -z "${ACTUALIZAR_NUEVO:-}" ]; then
    ACTUALIZAR_NUEVO=1 ACTUALIZAR_PADRON="$PADRON" \
      exec bash "$DIR/scripts/actualizar.sh" "$ROL"
  fi

  # ── Rutas y usuario de ESTE Pi ──
  echo ">> Ajustando rutas para el usuario $(whoami)..."
  sed -i "s#User=pi\$#User=$(whoami)#; s#/home/pi/raspberry-webcam-sync#$DIR#g" systemd/*.service
  sed -i "s#/home/pi/#$HOME/#g" config.ini
  if [ -n "$PADRON" ]; then
    sed -i "s#^padron *=.*#padron = $PADRON#" config.ini
  fi

  # ── apt sano antes de instalar ──
  # Si el Pi se apagó de golpe, la lista de paquetes puede quedar dañada
  # ("package cache file is corrupted" / "unable to parse package file").
  # En ese caso se borra y se baja de nuevo.
  echo ">> Revisando el instalador de paquetes (apt)..."
  sudo dpkg --configure -a || true
  if ! sudo apt-get update; then
    echo ">> La lista de paquetes estaba dañada: reparándola..."
    sudo rm -rf /var/lib/apt/lists/*
    sudo apt-get clean
    sudo apt-get update
  fi

  # ── Reinstalar lo de este Pi ──
  if [ "$ROL" = a ]; then
    sudo bash scripts/instalar_servidor.sh
    sudo bash scripts/instalar_camara.sh
  else
    sudo bash scripts/instalar_descargador.sh
    bash scripts/instalar_ihm.sh
  fi

  # ── Comando corto "actualizar" para la próxima vez ──
  sudo ln -sf "$DIR/scripts/actualizar.sh" /usr/local/bin/actualizar
  sudo ln -sf "$DIR/scripts/verificar.sh" /usr/local/bin/verificar
  sudo ln -sf "$DIR/scripts/probar_serie.sh" /usr/local/bin/probar_serie
  sudo chmod +x "$DIR/scripts/actualizar.sh" "$DIR/scripts/verificar.sh" "$DIR/scripts/probar_serie.sh"

  echo ""
  echo "========================================================"
  echo " Listo: actualizado a $(git log -1 --format='%h %s')"
  echo " La próxima vez escribí solo:  actualizar"
  echo " Para revisar que todo ande:    verificar"
  echo " Reiniciando en 10 s (Ctrl+C para cancelar)..."
  echo "========================================================"
  sleep 10
  sudo reboot
}

main "$@"
