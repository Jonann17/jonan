# jonan

Repositorio de proyectos de Jonathan. Cada carpeta es un proyecto independiente.

| Carpeta | Qué es |
|---|---|
| [`raspberry-webcam-sync/`](raspberry-webcam-sync/) | Sistema de webcam con dos Raspberry Pi y un piranómetro casero con Arduino. |
| [`sig-ft-propuestas/`](sig-ft-propuestas/) | Propuestas de cambios para [SIG-FT](https://github.com/luanccozer/SIG-FT) (migración de la interfaz a Qt6), guardadas como parches. |
| [`Lista 1/`](Lista%201/) | Ejercicios de programación en C (lista 1). |

---

## 📷 Sistema de webcam para Raspberry Pi (`raspberry-webcam-sync/`)

Un **Raspberry Pi con webcam** (Pi A) saca una foto cada 1 a 60 minutos, la
guarda y la sube a su propia **página web**. También crea una **red WiFi**
(`FotosPi`). Un **segundo Raspberry Pi** (Pi B) se conecta a esa red, **baja
todas las fotos** ordenadas por día y tiene una **interfaz gráfica** (PyQt6)
para controlar todo. Junto con cada foto se guarda la medición de un
**piranómetro casero con Arduino** (radiación solar).

```
Pi A: cámara + servidor web + hotspot WiFi  ── WiFi "FotosPi" ──►  Pi B: descargador + IHM
   │
   └── Arduino UNO (por cable USB) + celda solar 11×6 cm
```

### Lo principal

- **Fotos**: `padron<PADRON>_DDMMAAAA_HHMMSS.jpg`, en 1600×1200 (4:3, para la
  lente fisheye).
- **Captura bajo demanda**: la cámara arranca en espera. Se inicia, se detiene
  y se cambia el intervalo (1, 5, 10, 20, 30 min o 1 h) desde la IHM, sin
  reiniciar nada.
- **Hora**: el Pi A no tiene reloj propio, así que la IHM le manda la hora
  antes de empezar.
- **Página web** (`http://192.168.50.1:8000`): panel de estado, galería por
  día, descarga en ZIP y "Ver en vivo".
- **Piranómetro**: Arduino UNO conectado por **cable USB** (sin conversor de
  nivel) o por los pines GPIO. La radiación de cada foto queda en
  `mediciones.csv` y se grafica en la IHM.
- **Arranque automático**: todo levanta solo al prender y se reinicia solo si
  se cae.

### Instalar o actualizar un Pi

Con internet y **sin `sudo`**:

```bash
curl -sL https://raw.githubusercontent.com/Jonann17/jonan/claude/trusting-lamport-hd05q6/raspberry-webcam-sync/scripts/actualizar.sh | bash
```

Detecta si es el Pi A o el Pi B, instala lo que corresponde y reinicia. Deja
instalados tres comandos:

| Comando | Para qué |
|---|---|
| `actualizar` | Baja la última versión, reinstala y reinicia. |
| `verificar` | Revisa todo con ✅/❌ y muestra cómo arreglar lo que falle. |
| `probar_serie` | Prueba la comunicación con el Arduino. |

### Más información

- [`raspberry-webcam-sync/README.md`](raspberry-webcam-sync/README.md): guía
  completa (instalación manual, hotspot, piranómetro, solución de problemas).
- [`raspberry-webcam-sync/HANDOFF.md`](raspberry-webcam-sync/HANDOFF.md):
  resumen para retomar el proyecto en otra sesión o cuenta.
