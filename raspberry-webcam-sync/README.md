# 📷 Sistema de webcam para Raspberry Pi 3 B

Sistema para que **un Raspberry Pi con webcam** saque una foto **cada 10 minutos**,
la suba a una **página web (nube)**, y que **otro Raspberry Pi** se conecte y
**descargue todas las fotos** a su propio directorio.

Todo arranca **solo al prender** cada Raspberry y tiene **self-check**: si un
equipo se apaga y se prende, el programa vuelve a lanzarse automáticamente y
sigue trabajando desde donde quedó, sin perder ni repetir fotos.

---

## 🧩 Cómo funciona (las 3 partes)

```
   ┌────────────────────┐        sube fotos        ┌──────────────────────┐
   │  Raspberry #1      │  ─────────────────────▶  │   Servidor / "nube"  │
   │  CÁMARA (webcam)   │      HTTP /subir          │  (página web)        │
   │  foto cada 10 min  │                           │  guarda TODAS las    │
   └────────────────────┘                           │  fotos               │
                                                     └──────────┬───────────┘
                                                                │ descarga
                                                                ▼
                                                     ┌──────────────────────┐
                                                     │  Raspberry #2         │
                                                     │  DESCARGADOR          │
                                                     │  baja todas las fotos │
                                                     └──────────────────────┘
```

1. **Cámara** (`camara/camara.py`): saca la foto, la guarda en su carpeta local
   (su propia "nube") y la sube al servidor.
2. **Servidor** (`servidor/servidor.py`): recibe y guarda **todas** las fotos, y
   muestra una página web para verlas y descargarlas (una por una o todas en ZIP).
3. **Descargador** (`descargador/descargador.py`): el segundo Pi baja todas las
   fotos a su propia carpeta.

El **servidor** puede correr en cualquiera de los dos Pi o en una PC de la red.
Lo más simple: correr el servidor **en el mismo Pi del descargador**.

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

Editá **`config.ini`** en cada Raspberry. Lo más importante:

- `padron` → tu número de padrón.
- `[camara] url_servidor` y `[descargador] url_servidor` → la **IP del equipo
  que corre el servidor**. Por ejemplo `http://192.168.1.100:8000`.
- `carpeta_local` / `carpeta_nube` → dónde se guardan las fotos.

Para averiguar la IP del servidor, en ese equipo ejecutá: `hostname -I`.

---

## 🚀 Instalación

En cada Raspberry, cloná el repo en `/home/pi/raspberry-webcam-sync` y corré el
script correspondiente. (Si lo ponés en otra ruta, ajustá las rutas de los
archivos `.service` en `systemd/`.)

### Raspberry #1 — la cámara
```bash
sudo bash scripts/instalar_camara.sh
```

### Equipo servidor (la nube)
```bash
sudo bash scripts/instalar_servidor.sh
```

### Raspberry #2 — el descargador
```bash
sudo bash scripts/instalar_descargador.sh
```

Cada script instala las dependencias, activa el arranque automático al prender
(`systemctl enable`) y deja el programa corriendo.

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

## 📡 Opción: el servidor como hotspot propio (sin router)

Si no querés depender de un router, el **Pi del servidor puede crear su propia
red WiFi (hotspot)** y los demás dispositivos se conectan a esa red para subir y
descargar las fotos.

```
        ┌──────────────────────────────┐
        │  Raspberry SERVIDOR           │
        │  crea la red WiFi "FotosPi"   │   ← hotspot (IP fija 192.168.50.1)
        │  + corre el servidor :8000    │
        └───────────────┬──────────────┘
        se conectan a esa red WiFi:
          │                         │
   ┌──────┴───────┐          ┌──────┴────────┐
   │ Pi CÁMARA    │          │ Pi DESCARGADOR │
   │ (sube fotos) │          │ (baja fotos)   │   ← también un celular/PC
   └──────────────┘          └────────────────┘
```

**1) En el Pi servidor**, creá el hotspot:
```bash
sudo bash scripts/configurar_hotspot.sh
# o con tus datos:
sudo SSID="FotosPi" PASSWORD="miclave123" IP_AP="192.168.50.1" \
     bash scripts/configurar_hotspot.sh
```
Esto crea una red WiFi WPA2 con IP fija que **se levanta sola al prender el Pi**
(NetworkManager le da DHCP a los que se conecten). Instalá también el servidor en
este mismo Pi con `scripts/instalar_servidor.sh`.

**2) En config.ini** (de los tres equipos) apuntá al hotspot:
```ini
url_servidor = http://192.168.50.1:8000
```

**3) En el Pi de la cámara y en el del descargador**, conectate a esa red:
```bash
sudo SSID="FotosPi" PASSWORD="miclave123" bash scripts/conectar_a_hotspot.sh
```
Queda guardada y se reconecta sola al prender.

**Notas:**
- Cualquier celular o PC también puede conectarse a la red `FotosPi` y entrar a
  `http://192.168.50.1:8000` para ver y descargar las fotos.
- Al usar el WiFi interno como hotspot, ese Pi **ya no se conecta a otra red WiFi**
  por esa placa. Si además necesitás internet en el servidor, conectalo por
  **cable de red (Ethernet)**.
- Para apagar el hotspot: `sudo nmcli connection down hotspot-fotos`.

---

## 🖥️ Usar la página web

Desde cualquier navegador de la red, entrá a:

```
http://IP_DEL_SERVIDOR:8000
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
