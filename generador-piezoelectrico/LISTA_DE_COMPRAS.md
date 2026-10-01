# 🛒 Lista de compras — Pasarela piezoeléctrica de 9 baldosas

🎥 = estaba en la lista del video · ➕ = nuevo, para la pasarela

## ⚡ Electrónica

- [ ] 🎥 **Arduino UNO** — 1 (+ cable USB-B para programarlo)
- [ ] 🎥 **Pantalla LCD 16x2 con módulo I2C** — 1
- [ ] 🎥 **Discos piezo de 35 mm** — **64** (6 por baldosa = 54, + 10 de repuesto)
- [ ] 🎥 **Diodos 1N4007** — **50** (5 por baldosa = 45, + 5 de repuesto)
- [ ] 🎥 **Transistores BC547** — **12** (9, + 3 de repuesto)
- [ ] 🎥 **Kit de resistencias**, que incluya:
  - 9 × 47 kΩ (base de cada BC547)
  - 10 × 10 kΩ (9 base→GND + 1 del divisor)
  - 1 × 100 kΩ (divisor)
  - 1 × 1 kΩ (LED de demostración)
  - unas 22 kΩ y 68 kΩ (para ajustar la sensibilidad si hace falta)
- [ ] 🎥 **Capacitor 10 µF** — 1 (para el prototipo de una baldosa)
- [ ] ➕ **Capacitor electrolítico 220 µF, 63 V** — 1 (bus común)
- [ ] ➕ **LEDs rojos de 5 mm** — 5 (demostración, opcional)
- [ ] 🎥 **Porta-pilas 2 × 18650** — 1
- [ ] 🎥 **Celdas 18650** — 2 (de marca, con protección)
- [ ] ➕ **Cargador de 18650** — 1 (externo, o módulo TP4056 por celda)
- [ ] ➕ **Interruptor de encendido** — 1
- [ ] ➕ **Protoboard grande (830 puntos)** o **placa perforada 9×15 cm** — 1
  (la mini protoboard 🎥 sirve solo para el prototipo)

## 🔗 Cables y conexiones

- [ ] 🎥 **Jumpers** macho-macho (~40) y hembra-macho (4, para el LCD)
- [ ] 🎥 **Cable de conexión 22 AWG** rojo y negro — ~10 m (piezos dentro de cada baldosa)
- [ ] ➕ **Cable bipolar (2 hilos)** — ~25 m (de cada baldosa a la caja central)
- [ ] ➕ **Borneras de 2 polos** — 9 (para conectar/desconectar cada baldosa)
- [ ] ➕ **Tubo termorretráctil** surtido — 1 paquete
- [ ] ➕ **Etiquetas o cinta** para numerar los cables 1–9
- [ ] ➕ **Caja plástica** para el circuito, Arduino y baterías — 1 (~20×15×7 cm)

## 🪵 Estructura (9 baldosas)

- [ ] 🎥 **Acrílico transparente 30×30 cm, 5 mm** — **9** (pídelo ya cortado en la tienda)
- [ ] ➕ **MDF o madera 30×30 cm, 12 mm** — 9 (bases)
- [ ] ➕ **Listones de madera 2×2 cm** — ~12 m (marcos)
- [ ] ➕ **Topes de goma / espuma densa** — ~50 (5 por baldosa: 4 esquinas + centro)
- [ ] ➕ **Tornillos para madera 3,5 × 30 mm** — ~80
- [ ] ➕ **Cola de carpintero** — 1
- [ ] ➕ **Cinta antideslizante** — ~3 m (el acrílico resbala: ¡seguridad!)
- [ ] 🎥 **Barras de silicona** — ~20
- [ ] ➕ **Lija** (grano 120) — 2 hojas

## 🧰 Herramientas

- [ ] 🎥 **Kit de soldadura** (cautín, estaño, flux, soporte)
- [ ] 🎥 **Pistola de silicona**
- [ ] ➕ **Multímetro** (imprescindible para probar cada baldosa)
- [ ] ➕ **Pelacables y alicate de corte**
- [ ] ➕ **Taladro + brocas** y **destornillador**
- [ ] ➕ **Serrucho o sierra caladora** (si no te cortan la madera en la tienda)
- [ ] ➕ **Regla, escuadra y marcador**

## 💻 Software

- [ ] **Arduino IDE** (gratis)
- [ ] Librería **LiquidCrystal I2C** (Frank de Brabander)

---

### 💡 Consejos de compra

- **Compra primero lo de una baldosa** (6 piezos, 5 diodos, 1 BC547, 1 acrílico,
  1 base) y prueba. Cuando funcione, compra el resto.
- Los **piezos** vienen en paquetes de 10–50; es lo más barato comprarlos en cantidad.
- Pide el **acrílico y el MDF cortados a medida**: ahorra mucho trabajo y
  quedan derechos.
- Si quieres más energía, usa **8 piezos por baldosa** → 82 piezos en total.
