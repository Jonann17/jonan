# 📷 Sistema de webcam para Raspberry Pi 3 B

Sistema para que **un Raspberry Pi con webcam** saque una foto **cada 1 a 60
minutos** (el intervalo se elige desde la IHM), la suba a una **página web
(nube)**, y que **otro Raspberry Pi** se conecte y **descargue todas las fotos**
a su propio directorio. Junto con cada foto se guarda la medición de un
**piranómetro casero con Arduino** (radiación solar).

Todo arranca **solo al prender** cada Raspberry y tiene **self-check**: si un
equipo se apaga y se prende, el programa vuelve a lanzarse automáticamente y
sigue trabajando desde donde quedó, sin perder ni repetir fotos.

---

## 🧩 Cómo funciona (2 dispositivos)

La cámara y el servidor van en el **mismo Raspberry** (Pi A). Ese Pi también crea
su propia red WiFi (hotspot) y el **segundo Raspberry** (Pi B) se conecta a esa
red para descargar las fotos.

```
   ┌───────────────────────────────────────┐
   │  Pi A  —  CÁMARA + SERVIDOR + HOTSPOT  │
   │                                        │
   │  camara.py                             │
   │   • foto cada X min (desde la IHM)     │
   │   • la guarda en su directorio         │  ← fotos_camara  (su propio directorio)
   │   • la sube por localhost ─────┐       │
   │                                ▼       │
   │  servidor.py (la "nube")               │
   │   • guarda TODAS las fotos     ────────┼─→ nube_fotos     (su "nube")
   │   • página web + descargas             │
   │                                        │
   │  crea la red WiFi "FotosPi"            │  ← hotspot (IP fija 192.168.50.1)
   └────────────────────┬──────────────────┘
                        │  Pi B se conecta a esa red WiFi
                        ▼
   ┌───────────────────────────────────────┐
   │  Pi B  —  DESCARGADOR + IHM            │
   │   • baja todas las fotos a su carpeta  │  ← fotos_descargadas
   │   • interfaz gráfica para controlar    │
   └───────────────────────────────────────┘
```

1. **Cámara** (`camara/camara.py`, en Pi A): saca la foto, la guarda en su
   carpeta local (`fotos_camara`, su propio directorio) y la sube al servidor
   por `localhost` (no depende del WiFi).
2. **Servidor** (`servidor/servidor.py`, en Pi A): recibe y guarda **todas** las
   fotos en `nube_fotos` (la "nube"), y muestra una página web para verlas y
   descargarlas (una por una o todas en ZIP).
3. **Descargador** (`descargador/descargador.py`, en Pi B): se conecta al hotspot
   del Pi A y baja todas las fotos a su propia carpeta.

Así, en el Pi A las fotos quedan en **su propio directorio** *y* en **su nube**;
y cualquier celular o PC que se conecte a la red `FotosPi` también puede ver y
descargar las fotos desde `http://192.168.50.1:8000`.

---

## 📛 Nombre de las fotos (padrón + fecha)

Cada foto se llama:

```
padron<PADRON>_DDMMAAAA_HHMMSS.jpg
```

Por ejemplo, con padrón `0001` el 20 de agosto de 2026 a las 14:30:00:

```
padron0001_20082026_143000.jpg
```

- `DDMMAAAA` es la fecha (día-mes-año).
- `HHMMSS` es la hora, para que las fotos del mismo día no se pisen entre sí.

El número de padrón se configura en `config.ini`.

---

## ⚙️ Configuración

Editá **`config.ini`** en cada Raspberry. Ya viene listo para esta topología:

- `padron` → tu número de padrón.
- `[camara] intervalo_segundos` → intervalo inicial (después se cambia desde la IHM).
- `[arduino] puerto = auto` → usa el Arduino por USB si está enchufado ahí; si
  no, los pines GPIO 14/15 (ver la sección del piranómetro).
- **Pi A** (cámara + servidor): `[camara] url_servidor = http://127.0.0.1:8000`
  (localhost, porque la cámara y el servidor están en el mismo Pi).
- **Pi B** (descargador): `[descargador] url_servidor = http://192.168.50.1:8000`
  (la IP fija del hotspot del Pi A).
- `carpeta_local` / `carpeta_nube` → dónde se guardan las fotos.

---

## 🚀 Instalación

### Forma rápida (recomendada): un solo comando

En cada Raspberry, con internet (el Pi B, por cable Ethernet mientras se
instala) y **sin `sudo`**:

```bash
curl -sL https://raw.githubusercontent.com/Jonann17/jonan/claude/trusting-lamport-hd05q6/raspberry-webcam-sync/scripts/actualizar.sh | bash
```

El script `scripts/actualizar.sh`:

- clona o actualiza el repo en `~/jonan`;
- detecta si es el **Pi A** (tiene el hotspot `hotspot-fotos`) o el **Pi B**;
- ajusta rutas y usuario en `config.ini` y en los `.service` (los Pi no tienen
  por qué usar el usuario `pi`) y **conserva el padrón**;
- repara la lista de paquetes de apt si quedó dañada;
- reinstala lo que corresponde a ese Pi y lo reinicia.

Además deja instalados tres comandos cortos:

| Comando | Para qué |
|---|---|
| `actualizar` | Baja la última versión y reinstala (lo mismo de arriba). |
| `verificar` | Revisa todo con ✅/❌ y, si algo falla, muestra el comando que lo arregla. |
| `probar_serie` | Prueba la comunicación con el Arduino por partes (`probar_serie lazo` prueba solo la UART del Pi). |

El hotspot (Pi A) y la conexión al hotspot (Pi B) se configuran una sola vez
con los scripts de abajo.

### Forma manual

Si lo instalás a mano en otra ruta o con otro usuario, ajustá antes las rutas
de `config.ini` y de los archivos `.service` en `systemd/`.

#### Pi A — cámara + servidor + hotspot
```bash
sudo bash scripts/configurar_hotspot.sh    # crea la red WiFi "FotosPi"
sudo bash scripts/instalar_servidor.sh     # la nube (página web)
sudo bash scripts/instalar_camara.sh       # saca y sube las fotos
```

#### Pi B — descargador + IHM (interfaz gráfica)
```bash
sudo bash scripts/conectar_a_hotspot.sh    # se conecta a la red "FotosPi"
sudo bash scripts/instalar_descargador.sh  # baja todas las fotos
bash scripts/instalar_ihm.sh               # interfaz gráfica PyQt6
```

Cada script instala las dependencias, activa el arranque automático al prender
(`systemctl enable`) y deja el programa corriendo. El hotspot y las conexiones
WiFi también quedan configurados para levantarse solos al prender.

---

## 🖥️ IHM (interfaz gráfica en el Pi B)

El Pi B tiene una **interfaz gráfica hecha en PyQt6** (`ihm/ihm.py`) que se abre
sola al iniciar el escritorio. Desde ahí podés, sin tocar la terminal:

- Ver el **estado** del sistema con luces 🟢/🔴 (servidor, cámara, descargador)
  y el total de fotos.
- Ver la **galería** de fotos descargadas, agrupadas por día; clic en una
  miniatura para verla en grande.
- **Ajustar el intervalo entre fotos** de la cámara: elegís **1, 5, 10, 20 o
  30 minutos o 1 hora** y tocás *Aplicar*. Se lo envía al servidor y la cámara
  lo toma en el próximo ciclo, **sin reiniciar nada**.
- **Iniciar / Detener la captura.** El programa de la cámara arranca solo al
  prender el Pi A, pero **queda en espera**: recién saca fotos cuando tocás
  *▶ Iniciar captura*. Con *⏹ Detener* vuelve a la espera.
- **Ajustar la fecha y hora del Pi A** (no tiene internet ni pila de reloj):
  muestra la hora de los dos Pi y la diferencia; *Enviar hora al Pi de la
  cámara* la ajusta. Si tocás *Iniciar* sin haberla ajustado, la IHM avisa y
  ofrece enviarla antes.
- Ver la **radiación del piranómetro en vivo** (W/m² y tensión de la celda).
- Pestaña **Gráfico**: la medición del piranómetro de cada foto
  (`mediciones.csv`), filtrable por día.

Las pestañas son: **Control** (estado, captura, intervalo, hora, piranómetro),
**Fotos** (galería) y **Gráfico**.

Cómo funciona el cambio de intervalo:

```
IHM (Pi B)  --POST /config-->  Servidor (Pi A)  --lo guarda-->  .config_runtime.json
Cámara (Pi A)  --GET /config cada ciclo-->  usa el nuevo intervalo
```

Para abrir la IHM a mano:  `python3 ihm/ihm.py`

> El nombre de cada foto ya incluye **hora, minuto y segundo**:
> `padron<PADRON>_DDMMAAAA_HHMMSS.jpg` (los últimos 6 dígitos son HH-MM-SS).

---

## ☀️ Piranómetro casero (Arduino) en el Pi A

El Arduino le pasa los datos al Pi A por un puerto serie (cable USB o los
pines GPIO).

- Sketch: `arduino/piranometro/piranometro.ino` (abrir con el IDE de Arduino).
  Responde una línea JSON a `NOW` (lectura del momento) y a `GET` (resumen
  desde la foto anterior). Se puede probar solo con el Monitor Serie a 9600.
- Cableado por pines: **`arduino/esquematico_conexion.svg`** (se abre en el navegador).

> En Mac con chip Apple, si el IDE de Arduino da `bad CPU type in executable`
> al compilar, instalá Rosetta 2: `softwareupdate --install-rosetta --agree-to-license`.

### Opción 1 (recomendada): cable USB

Conectá el Arduino a un puerto USB del Pi A con el mismo cable que se usa para
programarlo. **No hace falta conversor de nivel** y el USB también alimenta al
Arduino. Con `puerto = auto` (en `config.ini`) la cámara lo encuentra sola en
`/dev/ttyACM0` (o `/dev/ttyUSB0` en los clones con chip CH340).

Abrir el puerto USB reinicia el Arduino UNO: la cámara espera 2,5 s antes de
la primera consulta y descarta el mensaje de bienvenida.

### Opción 2: pines GPIO 14/15 con conversor de nivel

El Pi trabaja a **3,3 V** y el Arduino a **5 V**: TX/RX pasan por un
**conversor de nivel bidireccional** (directo puede quemar el GPIO del Pi).

| Pi A (pin físico) | Conversor de nivel | Arduino UNO |
|---|---|---|
| pin 1 · 3V3 | LV | — |
| pin 2 · 5V | HV | 5V |
| pin 6 · GND | GND (ambos lados) | GND |
| pin 8 · GPIO14 (TXD) | LV1 → HV1 | D8 (RX) |
| pin 10 · GPIO15 (RXD) | LV2 ← HV2 | D9 (TX) |

Al programar el Arduino por USB, **desconectá el cable de 5V del Pi**.

Requiere la UART habilitada (`/dev/serial0`): `instalar_camara.sh` la activa
(o *Configuración de Raspberry Pi → Interfaces → Puerto serie: Activado,
Consola serie: Desactivado*) y después hay que reiniciar.

**Sin conversor**, también se puede con un divisor de tensión, con más cuidado:

- Arduino D9 (TX) → divisor **1 kΩ + 2 kΩ** → Pi pin 10 (RXD). Baja 5 V a 3,3 V.
  **Nunca directo.**
- Pi pin 8 (TXD) → Arduino D8 (RX), directo (el Arduino toma 3,3 V como "1").
- GND del Pi ↔ GND del Arduino, obligatorio.

Si no anda, `probar_serie` indica en qué parte está la falla: Pi, conversor,
cables o Arduino.

### Celda solar (como en el artículo)

```
Celda (+) ── R 10 kΩ ── A0        (la celda nunca más de 5 V)
Celda (−) ────────────── GND
```

`P = V² / R`, `Área = largo × ancho`, `G = P / Área × CAL_K` (W/m²).

El código original del artículo tiene errores que quedaron **corregidos** en
el sketch (el área daba 0 por división entera y además mm²→m² es /10⁶; usaba
`analogRead` crudo como si fueran voltios; la resistencia "10" en vez de
10 000 Ω; `sprintf("%f")` con un puntero sin memoria colgaba el UNO).

> ⚠ Aun corregida, la fórmula **no da la irradiancia real**: con la resistencia
> en serie hacia A0 casi no circula corriente (se mide la tensión en vacío de
> la celda) y la celda convierte ~15 % de la luz. Con 5 V, 10 kΩ y 110×60 mm (placa de 11×6 cm) da
> ≈0,4 W/m². Es un **índice** que sube y baja con el sol; para W/m² reales hay
> que calibrar `CAL_K` contra una referencia (otro piranómetro o una estación
> meteorológica cercana). Alternativa más lineal: `#define MODO_SHUNT 1`
> (resistencia de ~1 Ω en paralelo con la celda, mide la corriente de
> cortocircuito, proporcional al sol).

Ajustar en la sección 1 del sketch: `RESISTENCIA_OHM` (medida con el
multímetro), `CELDA_LARGO_MM`, `CELDA_ANCHO_MM` y `CAL_K`. Hoy está configurado
para la placa de **11 × 6 cm** con **10 kΩ**. La radiación (`g_*`) sale con 4
decimales porque con esta celda los valores son chicos.

Antes de dejarla al sol, medí con el multímetro la tensión de la placa a pleno
sol: si pasa de 5 V, en el JSON `sat` va a ser mayor que 0 y hay que agregar un
divisor de tensión.

### Dónde quedan las mediciones

Cada foto genera una fila (mismo `nombre` que la foto) en `mediciones.csv`:

- Pi A: `fotos_camara/mediciones.csv` y `nube_fotos/mediciones.csv`
  (también en `/mediciones.csv` de la web y dentro del ZIP).
- Pi B: `fotos_descargadas/mediciones.csv` (lo baja el descargador).

Columnas principales: `g_avg` (radiación media entre una foto y la anterior),
`g_min`/`g_max`, `g_now` (en el instante de la foto), `v_avg` (tensión de la
celda), `sat` (> 0 = la celda pasó del rango del ADC), `arduino_ok`.

Sin Arduino conectado, poné `habilitado = false` en `[arduino]` de
`config.ini`: la cámara sigue sacando fotos igual (con `arduino_ok = 0`).

---

## 🔁 Arranque automático y self-check

Se usan servicios **systemd**:

- `WantedBy=multi-user.target` → el programa **arranca solo cada vez que se
  prende** el Raspberry.
- `Restart=always` → si el programa se cae por cualquier error, systemd lo
  **vuelve a lanzar solo** a los 10 segundos (el "self check").

Además, cada programa **recuerda lo que ya hizo**:

- La cámara anota las fotos ya subidas; si el servidor estaba apagado, las
  reintenta subir cuando vuelve, sin perder ninguna.
- El descargador compara por nombre y **no vuelve a bajar** lo que ya tiene.

Así, tras un corte de luz o un reinicio, todo sigue funcionando solo.

> ⚠ **Excepción a propósito:** después de un reinicio la cámara queda **EN
> ESPERA** (no saca fotos). El Pi no tiene pila de reloj ni internet, así que
> su hora puede estar mal: hay que **ajustar la hora e iniciar desde la IHM**.

---

## 📡 El hotspot (sin router)

El **Pi A crea su propia red WiFi** (hotspot) para no depender de ningún router.
El Pi B (y cualquier celular/PC) se conecta a esa red para descargar las fotos.

El hotspot lo crea `scripts/configurar_hotspot.sh` (ya incluido en los pasos de
instalación de arriba). Podés personalizar el nombre, la clave y la IP:
```bash
sudo SSID="FotosPi" PASSWORD="miclave123" IP_AP="192.168.50.1" \
     bash scripts/configurar_hotspot.sh
```
Crea una red WiFi WPA2 con IP fija que **se levanta sola al prender el Pi**
(NetworkManager le da DHCP a quien se conecte). En los Pi 3 de este proyecto
se usa la red **abierta** (`ABIERTO=1`, ver la solución de problemas).

**Notas:**
- Cualquier celular o PC también puede conectarse a la red `FotosPi` y entrar a
  `http://192.168.50.1:8000` para ver y descargar las fotos.
- Al usar el WiFi interno como hotspot, el Pi A **ya no se conecta a otra red WiFi**
  por esa placa. Si además necesitás internet en el Pi A, conectalo por
  **cable de red (Ethernet)**.
- Para apagar el hotspot: `sudo nmcli connection down hotspot-fotos`.

### 🩹 Solución de problemas del hotspot (Pi 3 B)

El WiFi del Pi 3 (chip `brcmfmac`) es quisquilloso en modo Access Point. Estos
son los problemas reales que pueden aparecer y cómo se resuelven (el script
`configurar_hotspot.sh` ya los contempla):

- **`802.1X supplicant took too long to authenticate`** al crear el hotspot →
  falta configurar el **país del WiFi**. Solución:
  ```bash
  sudo raspi-config nonint do_wifi_country PY   # tu país (PY = Paraguay)
  sudo iw reg set PY
  ```
  Y conviene fijar un **canal** (el script usa el 6).

- **Un cliente (celular/otro Pi) no conecta**: error `4way_handshake` /
  `no secrets` / `Segredos foram requisitados` → suele ser la **clave que no
  coincide**. Verificá la clave real que está transmitiendo el hotspot:
  ```bash
  sudo nmcli -s -g 802-11-wireless-security.psk connection show hotspot-fotos
  ```
  Tras cambiar la clave, reiniciá el hotspot de verdad (`down` + `up`), no solo
  `up`:
  ```bash
  sudo nmcli connection down hotspot-fotos && sudo nmcli connection up hotspot-fotos
  ```
  Y en el cliente, borrá el perfil viejo antes de reconectar:
  `sudo nmcli connection delete FotosPi`.

- **Si aun con la clave correcta NO conecta ningún cliente** → el chip del Pi 3
  no logra negociar WPA2. La solución práctica es dejar la red **abierta** (sin
  contraseña), perfecto para un prototipo en una red local:
  ```bash
  sudo ABIERTO=1 bash scripts/configurar_hotspot.sh          # en el Pi A
  sudo ABIERTO=1 bash scripts/conectar_a_hotspot.sh          # en el Pi B
  ```

---

## 🖥️ Usar la página web

Conectate a la red WiFi `FotosPi` y, desde cualquier navegador, entrá a:

```
http://192.168.50.1:8000
```

Vas a ver:

- un **panel de estado** (servidor, cámara, descargador, piranómetro y hora);
- la **galería** de fotos agrupada por día, con enlace para bajar cada una;
- un botón para **descargar todas en un ZIP** (ordenadas por día);
- **Ver en vivo**: la imagen de la cámara actualizada cada 2 segundos.

---

## 🔧 Comandos útiles

```bash
# Actualizar este Pi a la última versión (reinstala y reinicia)
actualizar

# Revisar que todo ande (✅/❌)
verificar

# Probar la comunicación con el Arduino
probar_serie

# Ver estado de un servicio
systemctl status camara.service

# Ver los logs en vivo
journalctl -u camara.service -f

# Reiniciar / detener
sudo systemctl restart camara.service
sudo systemctl stop camara.service
```

---

## 🧪 Probar sin esperar 10 minutos

Desde la IHM elegí el intervalo de **1 minuto**, tocá *Iniciar captura* y
mirá los logs (`journalctl -u camara.service -f`). Para algo todavía más
rápido, en `config.ini` poné `intervalo_segundos = 20` en `[camara]` y
reiniciá el servicio.

---

## ✅ Requisitos

- Dos Raspberry Pi 3 B con Raspberry Pi OS (NetworkManager) y Python 3.
- Webcam USB reconocida en `/dev/video0` (probá con `fswebcam prueba.jpg`).
- Arduino UNO con `piranometro.ino` y una celda solar chica (opcional: sin
  Arduino, poné `habilitado = false` en `[arduino]`).
- Internet solo para instalar y actualizar (el Pi A por Ethernet; el Pi B por
  Ethernet mientras actualiza). En funcionamiento, todo va por el hotspot.

Para retomar el proyecto en otra sesión o cuenta, ver **`HANDOFF.md`**.
