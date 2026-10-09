#!/usr/bin/env bash
# Prueba la comunicación del Pi A con el Arduino, por partes, para saber
# dónde está la falla (Pi, conversor de nivel, cable o Arduino).
# Usa el mismo puerto que la cámara: el USB si el Arduino está enchufado
# ahí, si no los pines GPIO 14/15 (/dev/serial0).
#
# Uso:
#   probar_serie          → le pregunta "NOW" al Arduino y muestra qué vuelve
#   probar_serie lazo     → prueba SOLO el Pi: unir con un cable el pin 8
#                           (GPIO14/TX) con el pin 10 (GPIO15/RX) del Pi,
#                           SIN el conversor ni el Arduino conectados.
#
# Frena el servicio de la cámara mientras prueba (usa el mismo puerto) y lo
# vuelve a arrancar al final.

MODO="${1:-arduino}"
DIR="$(cd "$(dirname "$(readlink -f "$0")")/.." && pwd)"
if [ "$MODO" = lazo ]; then
  PUERTO=/dev/serial0
else
  PUERTO="$(cd "$DIR" && python3 -c 'from comun import cargar_config, puerto_arduino; c = cargar_config(); print(puerto_arduino(c.get("arduino", "puerto", fallback="auto")))' 2>/dev/null)"
  PUERTO="${PUERTO:-/dev/serial0}"
fi
echo ">> Puerto: $PUERTO"

if [ ! -e "$PUERTO" ]; then
  echo "❌ No existe $PUERTO."
  echo "   → Lo más simple: conectá el Arduino al Pi con el cable USB."
  echo "   → Para usar los pines: Configuración de Raspberry Pi → Interfaces →"
  echo "     Puerto serie: Activado, Consola serie: Desactivado, y reiniciar."
  exit 1
fi

echo ">> Frenando la cámara mientras pruebo (usa el mismo puerto)..."
sudo systemctl stop camara 2>/dev/null
trap 'echo ">> Volviendo a arrancar la cámara..."; sudo systemctl start camara 2>/dev/null' EXIT

sudo python3 - "$MODO" "$PUERTO" <<'EOF'
import sys, time
try:
    import serial
except ImportError:
    print("❌ Falta pyserial → actualizar")
    sys.exit(1)

modo, puerto = sys.argv[1], sys.argv[2]
s = serial.serial_for_url(puerto, 9600, timeout=2)
# Por USB, abrir el puerto reinicia el Arduino: esperar a que arranque.
time.sleep(2.5 if ("ACM" in puerto or "USB" in puerto or "by-id" in puerto) else 0.5)
s.reset_input_buffer()

if modo == "lazo":
    print(">> Prueba de lazo: mando 'HOLA123' por el pin 8 y escucho en el pin 10...")
    s.write(b"HOLA123\n")
    r = s.readline()
    print("   Recibido:", repr(r))
    if r.strip() == b"HOLA123":
        print("✅ La UART del Pi funciona. Si con el Arduino falla, el problema")
        print("   está en el conversor, los cables o el Arduino.")
    elif r:
        print("⚠️  Llegó algo distinto: ruido o velocidad mal configurada.")
    else:
        print("❌ No volvió nada. ¿El cable une el pin 8 con el pin 10?")
        print("   Si está bien puesto, la UART del Pi no está funcionando.")
    sys.exit(0)

print(">> Le mando 'NOW' al Arduino (3 intentos)...")
for i in range(3):
    s.reset_input_buffer()
    s.write(b"NOW\n")
    r = s.readline()
    print(f"   Intento {i+1}: {r!r}")
    if r.strip().startswith(b"{") and r.strip().endswith(b"}"):
        print("✅ El Arduino responde bien. El camino Pi ↔ conversor ↔ Arduino anda.")
        sys.exit(0)
    time.sleep(1)

if r.strip() == b"NOW":
    print("⚠️  El Pi se escucha a sí mismo (vuelve el mismo 'NOW'): TX y RX")
    print("   están unidos en algún lado, por ejemplo en el MISMO canal del conversor.")
elif r:
    print("⚠️  Llega algo pero no es el JSON: casi siempre es GND sin unir,")
    print("   o el lado de 3,3 V (LV) del conversor sin alimentar.")
else:
    if "ACM" in puerto or "USB" in puerto or "by-id" in puerto:
        print("❌ No llega nada por USB. ¿Está cargado piranometro.ino en el Arduino?")
        print("   Probalo desde la Mac con el Monitor Serie (9600, NOW) y otro cable USB.")
        sys.exit(0)
    print("❌ No llega nada del Arduino. Probá en este orden:")
    print("   1) probar_serie lazo   (¿anda la UART del Pi sola?)")
    print("   2) Medí con el multímetro el conversor (ver la guía).")
    print("   3) Revisá que TX y RX estén CRUZADOS:")
    print("      Pi pin 8 (TX) → conversor → Arduino pin 8 (RX)")
    print("      Pi pin 10 (RX) ← conversor ← Arduino pin 9 (TX)")
EOF
