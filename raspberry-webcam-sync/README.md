# 📷 Sistema de webcam para Raspberry Pi 3 B

Sistema para que **un Raspberry Pi con webcam** saque una foto **cada 10 minutos**,
la suba a una **página web (nube)**, y que **otro Raspberry Pi** se conecte y
**descargue todas las fotos** a su propio directorio.

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
   │   • foto cada 10 min                   │
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
   │  Pi B  —  DESCARGADOR                  │
   │   • baja todas las fotos a su carpeta  │  ← fotos_descargadas
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

- `DDMMAAAA` es la fecha (día-mes-año), como pediste.
- Se agrega `HHMMSS` (hora) para que las **144 fotos del día** no se pisen entre sí.

El número de padrón se configura en `config.ini`.

---

## ⚙️ Configuración

Editá **`config.ini`** en cada Raspberry. Ya viene listo para esta topología:

- `padron` → tu número de padrón.
- **Pi A** (cámara + servidor): `[camara] url_servidor = http://127.0.0.1:8000`
  (localhost, porque la cámara y el servidor están en el mismo Pi).
- **Pi B** (descargador): `[descargador] url_servidor = http://192.168.50.1:8000`
  (la IP fija del hotspot del Pi A).
- `carpeta_local` / `carpeta_nube` → dónde se guardan las fotos.

---

## 🚀 Instalación

En cada Raspberry, cloná el repo en `/home/pi/raspberry-webcam-sync`. (Si lo
ponés en otra ruta, ajustá las rutas de los archivos `.service` en `systemd/`.)

### Pi A — cámara + servidor + hotspot
```bash
sudo bash scripts/configurar_hotspot.sh    # crea la red WiFi "FotosPi"
sudo bash scripts/instalar_servidor.sh     # la nube (página web)
sudo bash scripts/instalar_camara.sh       # saca y sube las fotos
```

### Pi B — descargador + IHM (interfaz gráfica)
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
- **Ajustar el intervalo entre fotos** de la cámara: elegís los segundos y tocás
  *Aplicar*. Se lo envía al servidor y la cámara lo toma en el próximo ciclo,
  **sin reiniciar nada**.

Cómo funciona el cambio de intervalo:

```
IHM (Pi B)  --POST /config-->  Servidor (Pi A)  --lo guarda-->  .config_runtime.json
Cámara (Pi A)  --GET /config cada ciclo-->  usa el nuevo intervalo
```

Para abrir la IHM a mano:  `python3 ihm/ihm.py`

> El nombre de cada foto ya incluye **hora, minuto y segundo**:
> `padron<PADRON>_DDMMAAAA_HHMMSS.jpg` (los últimos 6 dígitos son HH-MM-SS).

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
(NetworkManager le da DHCP a quien se conecte).

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

Vas a ver la lista de fotos, un botón para **descargar todas en un ZIP**, y un
enlace para bajar cada una.

---

## 🔧 Comandos útiles

```bash
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

Para una prueba rápida, en `config.ini` poné `intervalo_segundos = 20` en la
sección `[camara]`, reiniciá el servicio y mirá los logs. Después volvé a
dejarlo en `600` (10 minutos).

---

## ✅ Requisitos

- Raspberry Pi OS (o Debian) con Python 3.
- Webcam USB reconocida en `/dev/video0` (probá con `fswebcam prueba.jpg`).
- Los tres equipos en la **misma red**.
