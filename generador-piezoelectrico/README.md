# ⚡ Generador piezoeléctrico de pisadas (Arduino + LCD)

Proyecto basado en el video: https://youtu.be/YZ4OBxyyqOg

Una **placa de acrílico** con **discos piezoeléctricos** debajo genera electricidad
cada vez que alguien la pisa. Un **Arduino UNO** cuenta las pisadas, mide la
tensión generada y la muestra en una **pantalla LCD I2C**. Todo funciona con
**baterías 18650**.

> ℹ️ No pude abrir el video desde este entorno, así que el circuito y el código
> están armados a partir de la lista de componentes. Si en el video algo está
> conectado distinto, avísame y lo ajusto.

---

## 🧩 Cómo funciona

```
  PISADA
    │
    ▼
 ┌──────────────┐   CA    ┌──────────────┐   CC    ┌───────────┐
 │ Piezos bajo  │ ──────▶ │ Puente de    │ ──────▶ │ Capacitor │──┬──▶ A0 (divisor 100k/10k) → mide voltios
 │ el acrílico  │         │ 4 × 1N4007   │         │ 10 µF     │  │
 └──────────────┘         └──────────────┘         └───────────┘  └──▶ BC547 → D2 → cuenta pasos
                                                                        │
                                       Arduino UNO ◀────────────────────┘
                                            │
                                            ▼
                                     LCD 16x2 I2C:  "Pasos: 37"
                                                    "12.4V 2680uJ"
```

1. Al pisar, los piezos se doblan y producen **corriente alterna** (pulsos + y −).
2. El **puente rectificador** (4 diodos 1N4007) la convierte en **continua**.
3. El **capacitor de 10 µF** guarda ese pulso.
4. El **BC547** se activa con cada pulso → el Arduino **cuenta una pisada**.
5. El **divisor de tensión** (100k + 10k) baja el voltaje para que el Arduino
   lo pueda **medir** sin dañarse (aguanta hasta ~55 V).
6. El Arduino calcula la energía de cada pisada (`E = ½·C·V²`) y la muestra.

---

## 🛒 Materiales

| Cant. | Componente | Para qué |
|---|---|---|
| 2 | Lámina de acrílico transparente (ej. 30×30 cm) | Base y tapa de la placa |
| 8–12 | Discos piezo de 35 mm | Generan la electricidad |
| 1 | Arduino UNO | Cerebro |
| 1 | LCD 16x2 con módulo I2C | Pantalla |
| 1 | Mini protoboard | Montar el circuito |
| — | Cables de conexión + jumpers | Conexiones |
| 1 | Capacitor electrolítico 10 µF (≥ 50 V) | Guarda la energía de la pisada |
| 4 (+1) | Diodos 1N4007 | Puente rectificador (+1 opcional para cargar batería) |
| 1 | Transistor BC547 | Detector de pisadas |
| 1 | Resistencia 100 kΩ | Divisor (arriba) |
| 1 | Resistencia 10 kΩ | Divisor (abajo) |
| 1 | Resistencia 22 kΩ | Base del BC547 |
| 1 | Resistencia 100 kΩ | Base del BC547 → GND |
| 1 | Porta-pilas 2 × 18650 | Alimentación |
| 2 | Celdas 18650 | Alimentación (7,4 V) |
| — | Pistola de silicona, kit de soldadura | Armado |

---

## 🔌 Conexiones

### 1) Los piezos (en paralelo)

Suelda todos los discos **en paralelo**: todos los cables **rojos** juntos
(centro blanco/cerámica) y todos los **negros** juntos (borde de bronce).

```
 rojo ──●──────●──────●──────●───── PZ+
        │      │      │      │
       [P1]   [P2]   [P3]   [P4] ...
        │      │      │      │
 negro ─●──────●──────●──────●───── PZ−
```

> Respeta la misma polaridad en todos; si uno queda invertido, resta energía a los demás.

### 2) Puente rectificador (4 × 1N4007)

La franja gris del diodo es el **cátodo (−)**.

Conecta cada diodo así (ánodo → cátodo):

| Diodo | Ánodo (sin franja) | Cátodo (franja) |
|---|---|---|
| D1 | PZ+ | **V+** |
| D2 | PZ− | **V+** |
| D3 | **GND** | PZ+ |
| D4 | **GND** | PZ− |

### 3) Capacitor, medición y detector de pisadas

```
 V+ ──┬──────────────┬───────────────┬──────────
      │              │               │
    (+)            [100k]          [22k]
   10µF              │               │
    (−)              ├──── A0        ├──── Base BC547
      │              │               │
      │            [10k]          [100k]
      │              │               │
 GND ─┴──────────────┴───────────────┴──── Emisor BC547

                                     Colector BC547 ──── D2 (Arduino)
```

**BC547** (cara plana hacia ti, patas abajo): **C – B – E** (izquierda a derecha).

> Las resistencias también **descargan** el capacitor entre pisada y pisada,
> para que cada pisada se mida desde cero.

### 4) LCD I2C

| LCD | Arduino |
|---|---|
| GND | GND |
| VCC | 5V |
| SDA | A4 |
| SCL | A5 |

### 5) Alimentación

| Porta-pilas 2×18650 | Arduino |
|---|---|
| + (7,4 V) | **VIN** |
| − | GND |

⚠️ **Todas las GND deben estar unidas** (Arduino, puente, capacitor, BC547, LCD, baterías).

### 6) (Opcional) Cargar la batería con los piezos

Un diodo 1N4007 extra desde **V+** (ánodo) hacia el **+ de la batería**
(cátodo) deja pasar la energía hacia la batería y evita que vuelva.
Ver la sección de *expectativas* abajo: es una demostración, no un cargador real.

---

## 🔨 Armado de la placa

1. Corta dos láminas de acrílico del mismo tamaño.
2. Pega los piezos sobre la lámina de **abajo** con un punto de silicona
   **solo en el borde** (el disco tiene que poder doblarse). Repártelos parejo.
3. Suelda los piezos en paralelo y saca dos cables (PZ+ y PZ−).
4. Pega pequeños "topes" de silicona en el **centro** de cada piezo:
   la lámina de arriba los presiona al pisar → más flexión → más voltaje.
5. Coloca separadores en las esquinas (silicona, goma o espuma) y pon la
   lámina de **arriba**. Tiene que quedar con un poco de juego.
6. Arma el circuito en la mini protoboard y conecta los dos cables.

---

## 💻 Programa

1. Instala el **Arduino IDE**.
2. Instala la librería: *Herramientas → Administrar bibliotecas →* busca
   **"LiquidCrystal I2C"** (de *Frank de Brabander*).
3. (Si la pantalla no muestra nada) carga `escaner_i2c/escaner_i2c.ino`, abre el
   Monitor Serie a 9600 y anota la dirección (0x27 o 0x3F).
4. Abre `generador_piezo/generador_piezo.ino`, cambia la dirección si hace falta:
   ```cpp
   LiquidCrystal_I2C lcd(0x27, 16, 2);
   ```
5. Selecciona **Arduino UNO** y súbelo.

En la pantalla verás:

```
Pasos:37
12.4V 2680uJ
```

- **Pasos**: pisadas contadas.
- **V**: tensión pico de la última pisada.
- **uJ / mJ**: energía total estimada que generó la placa.

En el Monitor Serie (9600) también se imprime cada pisada.

---

## 🛠️ Si algo falla

| Problema | Solución |
|---|---|
| LCD encendida pero sin letras | Gira el potenciómetro azul de atrás del módulo I2C (contraste) |
| LCD sin nada | Revisa SDA/SCL, usa el escáner I2C y cambia la dirección |
| No cuenta pasos | Revisa la orientación del BC547 (C-B-E) y que el colector vaya a D2 |
| Cuenta 2 pasos por pisada | Sube `ANTIRREBOTE_MS` en el código (ej. 400) |
| Voltaje siempre 0 | Revisa el puente de diodos (orientación) y la polaridad del capacitor |
| Voltaje muy bajo | Agrega topes en el centro de los piezos, más piezos, o pisa más fuerte |
| Arduino se reinicia | Batería baja: carga las 18650 (con cargador) |

---

## 📏 Expectativas realistas

- Cada pisada genera del orden de **micro-joules a milijoules**. Es suficiente
  para **encender LEDs por un instante** y para mostrar la medición, pero
  **no** para cargar de verdad una 18650 (harían falta cientos de miles de pisadas).
- Por eso el Arduino funciona con las baterías, y los piezos son la parte que
  se **mide y demuestra**.
- Para cargar las 18650 usa un **módulo TP4056** o un cargador USB.

## 🔒 Seguridad

- Las 18650 tienen mucha energía: **nunca** las pongas en cortocircuito,
  no las perfores y respeta la polaridad del porta-pilas.
- El capacitor electrolítico tiene polaridad: la franja marca el **−**.
- Los piezos pueden dar picos de **decenas de voltios** sin carga: no los
  conectes directo a un pin del Arduino.
