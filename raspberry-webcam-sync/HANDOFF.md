# 🧭 HANDOFF — Sistema de webcam Raspberry Pi

Documento de traspaso para retomar el proyecto en **cualquier cuenta/sesión de
Claude** (o por otra persona). Resume qué es, cómo está armado, cómo se instala,
qué problemas resolvimos y qué quedó pendiente.

- **Repositorio:** `Jonann17/jonan`
- **Rama de trabajo:** `claude/pi-webcam-image-sync-h8iusk`
- **Pull Request activo:** #2 → https://github.com/Jonann17/jonan/pull/2
- **Carpeta del proyecto:** `raspberry-webcam-sync/`

> Para continuar en otra cuenta: cloná el repo, abrí esta rama y leé este archivo.
> Todo el trabajo vive en GitHub; la conversación de chat no es necesaria.

---

## 1. Qué hace el sistema

Un Raspberry Pi con webcam saca una foto cada cierto intervalo, la guarda y la
sube a una "nube" (servidor web propio). Un segundo Raspberry se conecta por
WiFi y descarga todas las fotos, con una interfaz gráfica (IHM) para verlas y
configurar el sistema.

### Topología (2 dispositivos)
```
Pi A  =  CÁMARA + SERVIDOR + HOTSPOT WiFi        Pi B  =  DESCARGADOR + IHM
  - saca foto cada X min                           - se conecta al hotspot
  - la guarda en su directorio (fotos_camara)      - descarga TODAS las fotos
  - la sube por localhost al servidor              - las ordena por día
  - servidor = "nube" (web + API)                  - IHM PyQt6: ver/config
  - crea la red WiFi "FotosPi" (IP 192.168.50.1)
```
- Pi A: usuario `jonan`, repo en `/home/jonan/jonan/raspberry-webcam-sync`.
- Pi B: usuario `rpi`, repo en `/home/rpi/jonan/raspberry-webcam-sync`.
- Los dos son Raspberry Pi 3 B, con Raspberry Pi OS (NetworkManager / nmcli).
- País WiFi configurado: **PY (Paraguay)**.

### Nombre de las fotos
`padron<PADRON>_DDMMAAAA_HHMMSS.jpg` — ej. `padron0001_24092026_143005.jpg`
(incluye día, mes, año, y **hora-minuto-segundo**). Padrón configurable.

---

## 2. Estructura de archivos (`raspberry-webcam-sync/`)

| Archivo | Rol |
|---|---|
| `config.ini` | Configuración compartida (padrón, intervalo, rutas, URLs, resolución). |
| `comun.py` | Funciones compartidas: cargar config, logging, crear carpetas. |
| `camara/camara.py` | Saca la foto, la guarda local y la sube. Consulta el intervalo al servidor en cada ciclo (se puede cambiar en caliente). Reintenta subir pendientes tras reinicio. |
| `servidor/servidor.py` | Flask. Recibe/guarda fotos, página web con panel de estado + galería por día, "Ver en vivo", ZIP, y API (`/lista`, `/subir`, `/config`, `/estado`, `/latido`, `/vivo`). |
| `descargador/descargador.py` | Baja las fotos que faltan a subcarpetas por día; manda "latido" al servidor. |
| `ihm/ihm.py` | Interfaz gráfica PyQt6 (Pi B): estado con luces, galería, selector de intervalo. |
| `systemd/*.service` | Servicios de arranque automático + reinicio (self-check). |
| `scripts/instalar_*.sh` | Instaladores (cámara, servidor, descargador, IHM). |
| `scripts/configurar_hotspot.sh` | Convierte al Pi A en Access Point WiFi. |
| `scripts/conectar_a_hotspot.sh` | Conecta un Pi cliente a la red del hotspot. |
| `README.md` | Guía completa en español. |

---

## 3. Instalación (desde cero)

### Pi A — cámara + servidor + hotspot
```bash
sudo bash scripts/configurar_hotspot.sh    # crea la red WiFi "FotosPi"
sudo bash scripts/instalar_servidor.sh     # la nube (web)
sudo bash scripts/instalar_camara.sh       # saca y sube fotos
```

### Pi B — descargador + IHM
```bash
sudo bash scripts/conectar_a_hotspot.sh    # se une a "FotosPi"
sudo bash scripts/instalar_descargador.sh  # baja las fotos
bash scripts/instalar_ihm.sh               # interfaz gráfica PyQt6
```

> Importante: el `config.ini` trae rutas `/home/pi/...` y los `.service` traen
> `User=pi`. En estos Pi el usuario NO es `pi`, así que tras clonar hay que
> ajustar (ya se hizo en los Pi actuales):
> ```bash
> sed -i "s#/home/pi/#$HOME/#g" config.ini
> sed -i "s#User=pi#User=$(whoami)#; s#/home/pi/raspberry-webcam-sync#$HOME/jonan/raspberry-webcam-sync#g" systemd/*.service
> ```

### Actualizar a la última versión (en cada Pi)
```bash
cd ~/jonan/raspberry-webcam-sync
git pull origin claude/pi-webcam-image-sync-h8iusk
# Pi A:
sudo systemctl restart servidor camara
# Pi B:
sudo systemctl restart descargador
```

---

## 4. Configuración (`config.ini`)

- `[general] padron` → prefijo del nombre de las fotos.
- `[camara] intervalo_segundos` → intervalo (se puede cambiar en caliente desde la IHM).
- `[camara] resolucion` → **1600x1200 (4:3)** para aprovechar la lente fisheye.
- `[camara] resolucion_vivo` → 640x480 (para el "Ver en vivo", más fluido).
- `[camara] url_servidor` → `http://127.0.0.1:8000` (localhost, cámara+servidor en el mismo Pi).
- `[servidor] puerto` → 8000; `carpeta_nube` → dónde guarda todas las fotos.
- `[descargador] url_servidor` → `http://192.168.50.1:8000` (IP del hotspot).
- `[descargador] carpeta_local` → dónde se descargan (en subcarpetas por día).

El intervalo cambiado desde la IHM se guarda en `.config_runtime.json` (en la
carpeta de la nube) vía `POST /config`; la cámara lo lee con `GET /config`.

---

## 5. Red WiFi / hotspot — lecciones aprendidas (Pi 3)

El WiFi del Pi 3 (chip `brcmfmac`) es delicado en modo AP. Problemas y solución
(ya contemplados en `scripts/configurar_hotspot.sh`):

- **`802.1X supplicant took too long`** al crear el hotspot → faltaba fijar el
  **país WiFi**: `sudo raspi-config nonint do_wifi_country PY` + `sudo iw reg set PY`,
  y fijar un **canal** (usamos el 6).
- **Cliente no conecta** (`4way_handshake` / `no secrets` / `Segredos...`) →
  clave que no coincidía; hay que reiniciar el hotspot con `down` + `up` (no solo
  `up`) para que aplique, y en el cliente borrar el perfil viejo:
  `sudo nmcli connection delete FotosPi`.
- **Con WPA2 no conectaba ningún cliente** (ni iPhone ni Pi B) → **solución que
  funcionó: red ABIERTA (sin contraseña)**, válida para prototipo:
  ```bash
  sudo ABIERTO=1 bash scripts/configurar_hotspot.sh   # Pi A
  sudo ABIERTO=1 bash scripts/conectar_a_hotspot.sh   # Pi B
  ```
- Datos del hotspot: SSID `FotosPi`, IP fija `192.168.50.1`. El nombre interno
  de la conexión nmcli es `hotspot-fotos` (distinto del SSID, es normal).
- El Pi A, al ser hotspot, NO se conecta a otra WiFi por esa placa. Si necesita
  internet, va por cable Ethernet.

**Estado actual confirmado:** hotspot arriba en red ABIERTA, Pi B conecta y
descarga OK (ping a 192.168.50.1 responde, fotos bajan a subcarpetas por día).

---

## 6. IHM (PyQt6) en el Pi B — `ihm/ihm.py`

- Panel de **estado** con luces 🟢/🔴 (servidor, cámara, descargador) + total de fotos.
- **Galería** de fotos descargadas, agrupada por día; clic para ver en grande.
- Selector de **intervalo** con opciones fijas: **1, 5, 10, 20, 30 min y 1 hora**
  → botón *Aplicar* (POST a `/config`; la cámara lo toma sin reiniciar).
- La red corre en un hilo aparte para no congelar la UI; refresco cada 5 s.
- Se instala con `scripts/instalar_ihm.sh` (PyQt6 por apt, o pip como fallback) y
  queda en autostart del escritorio. Abrir a mano: `python3 ihm/ihm.py`.

---

## 7. API del servidor (para referencia)

| Ruta | Método | Qué hace |
|---|---|---|
| `/` | GET | Página web: estado, galería por día, botones. |
| `/subir` | POST | La cámara sube una foto (campo `foto`). |
| `/lista` | GET | JSON con los nombres de todas las fotos. |
| `/foto/<nombre>` | GET | Descarga una foto. |
| `/descargar_todo` | GET | ZIP con todas (ordenadas por día). |
| `/config` | GET/POST | Lee/cambia el intervalo de la cámara (segundos, 5..86400). |
| `/estado` | GET | JSON con estado del sistema (para la IHM). |
| `/latido` | POST | El descargador avisa que está vivo. |
| `/vivo` | GET | Foto del momento (para "Ver en vivo"). |
| `/envivo` | GET | Página que refresca la imagen cada 2 s. |

---

## 8. Pendiente / próximos pasos sugeridos

- [ ] **Probar el reinicio** de ambos Pi para confirmar el self-check
      (que hotspot, cámara, servidor y descargador levanten solos al prender).
- [ ] Ajustar fino la resolución fisheye si 1600x1200 no la soporta la webcam
      (ver `v4l2-ctl --list-formats-ext -d /dev/video0`).
- [ ] Opcional: IHM en **pantalla completa** para la pantallita táctil del Pi.
- [ ] Opcional: volver el hotspot a **WPA2 con contraseña** si se resuelve la
      compatibilidad, o dejarlo abierto para el prototipo.
- [ ] Opcional: reordenar las fotos viejas del descargador (las que quedaron
      sueltas antes de la agrupación por día).

---

## 9. Cómo continuar en otra cuenta de Claude

1. Asegurate de que la otra cuenta tenga acceso al repo `Jonann17/jonan`
   (o hacelo público un rato para clonar).
2. En una sesión nueva, pedile a Claude que clone la rama y lea este archivo:
   ```
   git clone -b claude/pi-webcam-image-sync-h8iusk https://github.com/Jonann17/jonan.git
   ```
   y "leé `raspberry-webcam-sync/HANDOFF.md` para retomar el proyecto".
3. Con eso, Claude tiene todo el contexto para seguir.
