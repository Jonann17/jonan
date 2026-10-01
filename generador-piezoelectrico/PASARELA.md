# 🚶 Pasarela piezoeléctrica de 9 baldosas

Versión grande del proyecto: **9 baldosas de 30×30 cm** en fila (**2,7 m** de
largo). El Arduino sabe **qué baldosa pisas**, cuenta los pasos, calcula la
**dirección** y la **velocidad** con la que cruzas, y mide la energía total
generada.

> 🛒 Lista de compras completa: [LISTA_DE_COMPRAS.md](LISTA_DE_COMPRAS.md)

> 💡 **Primero arma y prueba UNA baldosa** con el sketch `generador_piezo`
> (ver [README.md](README.md)). Cuando funcione, haz las otras 8 iguales.

---

## 🧩 Cómo funciona

```
 Baldosa 1   Baldosa 2           Baldosa 9
 [piezos]    [piezos]    ...     [piezos]
    │           │                   │
 puente 1    puente 2            puente 9        ← 4 × 1N4007 cada uno
    │ V1        │ V2                │ V9
    ├─▶ BC547 ─▶ D2                 ├─▶ BC547 ─▶ D10   ← "¿qué baldosa se pisó?"
    │           │                   │
   ▶|          ▶|                  ▶|            ← diodo de aislamiento
    └───────────┴──────── … ────────┘
                     │
                   BUS ──┬── capacitor 220 µF
                         └── divisor 100k/10k ─▶ A0   ← "¿cuánta energía hay?"
```

**¿Por qué un puente y un diodo de aislamiento por baldosa?**

- Si juntas los piezos de todas las baldosas antes de rectificar, las baldosas
  que **no** estás pisando absorben la energía de la que sí pisas.
- El **diodo de aislamiento** separa cada baldosa del bus. Así el detector de
  cada baldosa solo ve **su propia** pisada, aunque el bus ya esté cargado.

---

## 🛒 Materiales (para 9 baldosas)

| Cant. | Componente | Notas |
|---|---|---|
| 54–72 | Discos piezo 35 mm | 6–8 por baldosa (compra ~10 de repuesto, se rompen) |
| 9 | Acrílico 30×30 cm, **5 mm** | Tapa de cada baldosa |
| 9 | MDF / madera 30×30 cm, 9–15 mm | Base de cada baldosa |
| — | Listones de madera ~2×2 cm | Marco de cada baldosa |
| — | Goma / espuma densa | Topes (4 esquinas + centro de cada baldosa) |
| 45 | Diodos 1N4007 | 4 del puente + 1 de aislamiento, por baldosa |
| 9 | Transistores BC547 | Un detector por baldosa |
| 9 | Resistencias 47 kΩ | Base del BC547 |
| 10 | Resistencias 10 kΩ | 9 base→GND + 1 del divisor |
| 1 | Resistencia 100 kΩ | Divisor del bus |
| 1 | Capacitor electrolítico **220 µF, 63 V** | Bus común (nuevo; ver nota) |
| 1 | Protoboard **grande (830 puntos)** o placa perforada | La mini no alcanza |
| — | Cable de 2 hilos (~3 m por baldosa) | O cable UTP: 8 hilos = 4 baldosas |
| 1 | Arduino UNO, LCD I2C, porta-pilas 2×18650 + 2 celdas | Igual que antes |

> Si solo tienes el capacitor de **10 µF**, también funciona: cambia en el
> código `C_BUS_F = 10e-6;`. Con 220 µF la energía se acumula y puedes
> hacer destellar LEDs.

---

## 🔌 Circuito

### Por cada baldosa (repetir 9 veces)

```
 PZ+ ─┐
      ├── Puente 4×1N4007 ──┬── Vn ──[47k]──┬── Base BC547
 PZ− ─┘          │          │                │
                GND         │              [10k]
                            │                │
                            │   GND ─────────┴── Emisor BC547
                            │
                            │        Colector BC547 ──── Pin Dn del Arduino
                            │
                            └──▶|── BUS   (1N4007: ánodo en Vn, franja hacia el BUS)
```

Puente (igual que en la placa de prueba):

| Diodo | Ánodo (sin franja) | Cátodo (franja) |
|---|---|---|
| D1 | PZ+ | Vn |
| D2 | PZ− | Vn |
| D3 | GND | PZ+ |
| D4 | GND | PZ− |

> Con 47k / 10k el BC547 se activa a partir de ~3,7 V. Así ignora las
> vibraciones pequeñas de las baldosas vecinas. Si no detecta tus pasos, baja
> la de 47k a 22k.

### Bus común (una sola vez)

```
 BUS ──┬──────────────┐
       │              │
     (+)           [100k]
    220µF             ├──── A0
     (−)           [10k]
       │              │
 GND ──┴──────────────┘
```

### Pines del Arduino

| Baldosa | Pin | | Otro | Pin |
|---|---|---|---|---|
| 1 | D2 | | LCD SDA | A4 |
| 2 | D3 | | LCD SCL | A5 |
| 3 | D4 | | Bus (divisor) | A0 |
| 4 | D5 | | Baterías + | VIN |
| 5 | D6 | | GND común | GND |
| 6 | D7 | | | |
| 7 | D8 | | | |
| 8 | D9 | | | |
| 9 | D10 | | | |

⚠️ **El orden importa**: la baldosa 1 va en un extremo y la 9 en el otro,
en fila. Si no, la dirección y la velocidad salen mal.
⚠️ **Todas las GND unidas.**

---

## 🔨 Armado de cada baldosa

```
  vista lateral
  ┌──────────────────────────────┐ ← acrílico 5 mm
  │ ▪        ▪        ▪        ▪ │ ← topes de silicona en el centro de cada piezo
  │═══      ═══      ═══      ═══│ ← piezos (pegados solo por el borde)
 █│                              │█ ← tope de goma en esquinas y centro
 █└──────────────────────────────┘█ ← base MDF + marco de listones
```

```
  vista de arriba (6 piezos)
  ┌─────────────────────┐
  │  ◯      ◯      ◯    │
  │          ▪          │  ▪ = tope de goma central
  │  ◯      ◯      ◯    │
  └─────────────────────┘
```

1. Corta las 9 bases de MDF y arma un marco de listones en cada una.
2. Pega los piezos en la base con silicona **solo en el borde**.
3. Suéldalos **en paralelo** (rojos juntos, negros juntos) y saca 2 cables.
   **Marca cada cable con el número de baldosa.**
4. Pon un punto de silicona en el **centro** de cada piezo (el acrílico lo apretará).
5. Pon los **topes de goma** en las esquinas y el centro. Tienen que ser
   **apenas 1–2 mm más altos** que los piezos con su punto de silicona: así el
   acrílico dobla los piezos, pero el peso de la persona lo aguantan los topes.
   Sin topes, los piezos se rompen.
6. Coloca el acrílico encima (que apoye en el marco y los topes).
7. Pon las 9 baldosas en fila y lleva los cables a una **caja central** con el
   circuito, el Arduino, el LCD y las baterías.

---

## 💻 Programa

1. Carga `pasarela/pasarela.ino` (necesita la librería **LiquidCrystal I2C**).
2. Si tus baldosas no miden 30 cm, cambia `LARGO_BALDOSA_M`.

### Lo que muestra la pantalla

```
|.#.......| >        ← línea 1: mapa en vivo (# = baldosa pisada) y dirección
Pasos: 152           ← línea 2: cambia cada 3 segundos
```

La línea 2 va rotando:

| Pantalla | Ejemplo | Qué es |
|---|---|---|
| Pasos | `Pasos: 152` | Pisadas totales |
| Velocidad | `Vel: 1.24 m/s` | Velocidad del último cruce completo |
| Energía | `18.5V 37.6mJ` | Tensión del bus y energía guardada en el capacitor |
| Cruces | `Cruces: 12` | Veces que alguien cruzó toda la pasarela |

- **Dirección:** `>` = de la 1 a la 9, `<` = de la 9 a la 1.
- **Cruce:** cuenta cuando pisas una punta y después la otra, en menos de 15 s.
- En el **Monitor Serie** (9600) se ven los pasos de cada baldosa y cada cruce.

---

## 🛠️ Si algo falla

| Problema | Solución |
|---|---|
| Una baldosa no cuenta | Prueba esa baldosa sola con `generador_piezo`. Revisa su puente y su BC547 |
| Una pisada cuenta en 2 baldosas | Sube el umbral: 47k → 68k, o separa un poco las baldosas |
| Cuenta 2 pasos por pisada | Sube `ANTIRREBOTE_MS` (ej. 800) |
| Dirección al revés | Las baldosas 1 y 9 están cambiadas de lugar |
| El bus no sube | Revisa la orientación de los diodos de aislamiento (franja hacia el BUS) |
| Se rompen los piezos | Los topes de goma están muy bajos; súbelos |

---

## 📏 Expectativas

Con 9 baldosas hay más energía que con una, pero sigue siendo poca: alcanza
para **destellos de LEDs** y para la medición. El Arduino sigue funcionando
con las 18650. Para LEDs de demostración, conecta en el bus un **LED rojo con
una resistencia de 1 kΩ** en serie: va a destellar con cada paso cuando el bus
tenga algunos voltios.
