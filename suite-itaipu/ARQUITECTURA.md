# Suite Itaipu: propuesta de arquitectura

Una suite estilo Office 365 que reúne **DocManager**, **SIG-FT** y **Corella Suite**:
un lanzador desde el que se instala, actualiza y abre cada app, y una capa
común que permite que las apps trabajen juntas.

> Estado: **propuesta para discutir.** Todavía no hay código. Está basada en la
> lectura de los tres repos (`luanccozer/DocManager`, `luanccozer/SIG-FT`,
> `rafhagmm/Corella_automation`) en octubre de 2026.

---

## 1. Lo que hay hoy

| | DocManager | SIG-FT | Corella Suite |
|---|---|---|---|
| Qué hace | Status real de los documentos del Aconex, mapa de planos, atrasos, dashboard | Fichas técnicas de repuestos en el Portal PMIB, RPA, AutoSpec con IA | Extrae LMUC, genera part list en Word, registra specifications en el Corella (Aras) |
| Interfaz | **customtkinter** + Dash | **PySide6** (Qt) | **PySide6** (Qt) |
| Datos externos | API Aconex | Portal PMIB, export Aconex, Gemini | Corella, API Aconex |
| Distribución | Inno Setup + GitHub Releases (repo privado, token embebido, SHA256) | Inno Setup + GitHub Releases | PyInstaller; solo avisa de versión nueva |
| Carpeta de datos | `Documentos\DocManager_Itaipu\` | `Documentos\SIG-FT\` | ajustes propios |

Lo que ya comparten **copiado y pegado** (y que hoy se mantiene tres veces):

- `rede.py`: salir por Zscaler/VPN/PAC con los certificados de Windows (~1.500 líneas entre las tres copias).
- Actualizador contra GitHub Releases (~1.100 líneas entre las tres).
- "Novidades", identidad de Windows, ofuscación, logs.
- **Cliente del Aconex**: el de Corella (`aconex_api/`) es un port del de DocManager.
- Motor de navegador: `sigft/core/rpa/navegador.py` dice explícitamente que sus reglas vienen del Corella.

Y un dato clave que ya enlaza dos de ellas: en `corella_suite/core/aconex.py`,

```
Aconex "Controle do Emissor"  ==  Corella "Document Number"
```

Ese código CMI/GE (`089341…`) es la **llave natural** de la suite.

---

## 2. Decisión principal: suite federada, no un monolito

Fusionar las tres apps en un solo ejecutable **no** conviene:

- Usan frameworks de interfaz distintos (customtkinter vs Qt).
- Las dependencias son pesadas y muy distintas (Playwright, ctranslate2, LLMs, pywin32, Dash…). Un instalador único obligaría a todos a bajar todo.
- Cada una tiene dueño, repo, ritmo de releases y tests propios. Un monolito acopla los ritmos de los tres equipos.

Lo que se propone es lo mismo que hace Office: **apps separadas + lanzador + capa común + contratos de datos.**

```
                 ┌──────────────────────────────────────────┐
                 │        Suite Itaipu (lanzador, Qt)        │
                 │  catálogo · instalar · actualizar · abrir │
                 │  bandeja de "pendientes entre apps"       │
                 └───────┬──────────────┬──────────────┬─────┘
                         │ lanza con    │ argumentos   │ (deep links)
                 ┌───────▼─────┐ ┌──────▼──────┐ ┌─────▼────────┐
                 │ DocManager  │ │   SIG-FT    │ │ Corella Suite│
                 └───────┬─────┘ └──────┬──────┘ └─────┬────────┘
                         │   lee/escribe contratos     │
                 ┌───────▼─────────────▼───────────────▼────────┐
                 │  Documentos\Suite_Itaipu\  (datos compartidos) │
                 │  suite.json · credenciais · aconex/snapshot ·  │
                 │  intercambio/*.json · logs                     │
                 └───────────────────────────────────────────────┘
                 ┌───────────────────────────────────────────────┐
                 │  paquete `itaipu_comum` (pip, versionado)      │
                 │  rede · atualizacao · credenciais · aconex ·   │
                 │  navegador · contratos · tema                  │
                 └───────────────────────────────────────────────┘
```

Reglas:

1. **Ninguna app importa el código de otra.** Se hablan solo por contratos (archivos JSON/xlsx versionados en la carpeta compartida) y por argumentos de línea de comandos.
2. **Cada app sigue funcionando sola**, sin el lanzador y sin las otras instaladas. La integración suma, nunca es requisito (Corella ya sigue esta regla con `aconex.disponivel()`).
3. **Sin servidor.** Todo local, en la máquina del usuario, porque la red corporativa (Zscaler, VPN) ya da bastante trabajo.

---

## 3. Las piezas

### 3.1 El lanzador ("Suite Itaipu")

App Qt pequeña (PySide6, como dos de las tres apps):

- **Catálogo**: lee un `catalogo.json` con cada app (nombre, repo, ícono, descripción, si requiere red de la empresa).
- **Instalar / actualizar / desinstalar**: baja el instalador del último release, verifica el SHA256 del manifiesto y lo ejecuta en silencio, por usuario (`/VERYSILENT /CURRENTUSER`, sin pedir admin). DocManager ya publica un manifiesto con SHA256; se estandariza para las tres.
- **Abrir**: lanza el `.exe` instalado, con argumentos si viene de un enlace entre apps.
- **Bandeja de pendientes**: muestra lo que una app dejó para otra (ver §4).
- **Estado**: versión instalada de cada una, si hay nueva, credenciales del Aconex configuradas o no.

Contrato que cada app debe cumplir para entrar al catálogo (`release-manifest.json` en cada release):

```json
{
  "app": "docmanager",
  "versao": "3.4.0",
  "instalador": "DocManager_Itaipu_Setup_3.4.0.exe",
  "sha256": "…",
  "args_silencioso": ["/VERYSILENT", "/CURRENTUSER", "/NORESTART"],
  "executavel": "DocManager.exe",
  "suite_contrato": 1
}
```

Al instalar, cada app se registra en `Documentos\Suite_Itaipu\suite.json` (ruta del exe, versión), y así el lanzador y las otras apps saben qué hay instalado.

### 3.2 El paquete común `itaipu_comum`

Repo propio, publicado como wheel. Se adopta **app por app**, sin big bang: cada app reemplaza su copia de un módulo por el del paquete cuando le convenga.

| Módulo | Sale de | Por qué primero |
|---|---|---|
| `rede` | las 3 copias de `rede.py` | Es la parte más frágil y la que más se repite |
| `atualizacao` | `updater.py` de DocManager (el más completo) | Lo usa también el lanzador |
| `credenciais` | DocManager (DPAPI) | Cargar las credenciales del Aconex **una sola vez** para toda la suite |
| `aconex` | `aconex_backend.py` / `aconex_api/` | Un cliente, una autenticación, un caché |
| `navegador` | `sigft/core/rpa/navegador.py` + Corella | Las mismas reglas de Playwright en el PMIB y en el Corella |
| `contratos` | nuevo | Esquemas (pydantic) de los archivos de intercambio |
| `tema` | tokens de Corella / SIG-FT | Que las apps se vean de la misma familia |

### 3.3 Carpeta compartida `Documentos\Suite_Itaipu\`

```
Suite_Itaipu\
  suite.json              apps instaladas, versiones, rutas
  credenciais.json        Aconex (cifrado DPAPI, como hoy en DocManager)
  aconex\
    snapshot.parquet      última extracción completa (la hace DocManager)
    snapshot.meta.json    fecha, usuario, cantidad de filas
  intercambio\
    corella_cadastros.json     lo que Corella registró
    pendentes_corella.json     lo que DocManager sugiere registrar
    ...
  logs\
```

---

## 4. Las interconexiones

Ordenadas de más concreta (ya vemos la llave en el código) a más hipotética (hay que validarla con los usuarios).

### A. Aconex una sola vez (DocManager → Corella, SIG-FT)

DocManager ya baja el historial completo del Aconex (~80.000 filas, ~9.500 documentos). Hoy Corella vuelve a consultar el Aconex documento por documento para validar el "Controle do Emissor", y SIG-FT trabaja con un export manual del Aconex (lista de precios, `pmib_manager`).

**Propuesta:** DocManager guarda la extracción en `aconex\snapshot`. Corella valida primero contra el snapshot (instantáneo y sin red) y solo va a la API si el documento no está o el snapshot es viejo. SIG-FT lee la lista de precios del snapshot en vez de pedir un export.

Ganancia: una sola credencial, una sola extracción, menos llamadas a la API.

### B. Lo que Corella registró aparece en DocManager (Corella → DocManager)

Al terminar un lote, Corella escribe en `intercambio\corella_cadastros.json`: Document Number (= Controle do Emissor), Engineering Document ID, Part ID, fecha y estado (incluido "en duda").

DocManager, que ya cruza por código CMI, suma una columna **"Corella"** en Status y Doc List: registrado / en duda / no registrado.

### C. Pendientes de registrar en Corella (DocManager → Corella)

DocManager sabe qué documentos llegaron a revisión aprobada y tienen código GE (`089341…`). Cruzado con B, sale la lista de **"aprobado en el Aconex, todavía no está en el Corella"**.

Esa lista va a `intercambio\pendentes_corella.json`, aparece en la bandeja del lanzador y, con un clic, abre Corella con la cola ya cargada (`CorellaSuite.exe --fila pendentes_corella.json`).

Es el ejemplo más claro de "apps que se acompañan": una detecta el trabajo, la otra lo ejecuta, y la primera ve el resultado.

### D. Enlaces entre apps (deep links)

Un protocolo `itaipu-suite://` registrado por el lanzador:

- `itaipu-suite://docmanager/documento/089341…` → DocManager abierto en ese documento.
- `itaipu-suite://corella/fila?arquivo=…` → Corella con la cola cargada.
- `itaipu-suite://sigft/ficha/<codigo>` → SIG-FT en la ficha.

En los reportes Excel de cada app, el código pasa a ser un hipervínculo a la otra.

### E. Motor de RPA compartido (SIG-FT ↔ Corella)

Ya hay transferencia de conocimiento (SIG-FT copió reglas del Corella). Juntarlo en `itaipu_comum.navegador` hace que un arreglo hecho por un equipo (timeouts, Zscaler, perfil del navegador, descarga de Chromium detrás del proxy) les llegue a los dos.

### F. Material: SIG-FT ↔ Corella (hipótesis, **validar**)

Las dos trabajan con materiales/repuestos: SIG-FT con fichas técnicas en el PMIB y Corella con códigos LMUC y Engineering Part IDs. Si existe una tabla que relacione **código LMUC ↔ material PMIB**, se podría:

- Desde Corella, "ver la ficha técnica de este material" en SIG-FT.
- Desde SIG-FT, reutilizar las descripciones EN/PT-BR que Corella extrae del LMUC.

No encontré esa llave en el código. **Hay que preguntarle a quien usa las dos** antes de construir nada.

---

## 5. Fases

| Fase | Entrega | Toca las apps |
|---|---|---|
| **0. Acuerdos** | Dueños de cada repo de acuerdo, nombre, repo de la suite, convención de releases (`release-manifest.json`), token de solo lectura | Solo agregar el manifiesto al workflow de release |
| **1. Lanzador MVP** | Catálogo, instalar/actualizar/abrir las tres apps | No |
| **2. `itaipu_comum` v0** | `rede` + `credenciais` + `atualizacao`; el lanzador lo usa primero | Opcional, app por app |
| **3. Aconex compartido** | Credenciales únicas + snapshot (A) | DocManager escribe, Corella lee |
| **4. Flujo DocManager ⇄ Corella** | B + C + bandeja de pendientes | Las dos |
| **5. Deep links y RPA común** | D + E | Las tres |
| **6. Material** | F, si se valida | SIG-FT + Corella |

La fase 1 da un resultado visible sin tocar ninguna app, y de ahí en adelante cada fase se puede usar por separado.

---

## 6. Riesgos y puntos abiertos

- **Repos de otras personas.** DocManager y SIG-FT son de `luanccozer` y Corella de `rafhagmm`. Las fases 2 a 6 necesitan que estén de acuerdo; la 1 no.
- **Token embebido.** Hoy DocManager embebe en el exe un token para leer releases de un repo privado, y cualquiera puede extraerlo de un binario. Para la suite conviene **un único token fine-grained, de solo lectura de releases**, o publicar los instaladores en un lugar que no lo requiera (repo de releases aparte, carpeta de red de la empresa).
- **TI corporativa.** Instalar en silencio, ejecutables sin firmar (SmartScreen) y registrar un protocolo `itaipu-suite://` puede chocar con políticas de TI. Instalar por usuario evita pedir admin; la firma de código resolvería SmartScreen para las cuatro de una vez (un solo certificado).
- **Dos frameworks de interfaz.** El lanzador en Qt puede abrir DocManager (customtkinter) sin problema, porque son procesos separados. Migrar DocManager a Qt es una decisión aparte y no hace falta para la suite.
- **Versiones del contrato.** Cada archivo de intercambio lleva `"contrato": N`; una app que lee una versión que no conoce la ignora y avisa, nunca se rompe.

---

## 7. Preguntas para arrancar

1. ¿Dónde vive la suite: un repo nuevo (recomendado, p. ej. `Suite-Itaipu`) o una carpeta acá?
2. ¿Los dueños de DocManager y Corella ya están al tanto o la fase 1 tiene que hacerse sin tocar sus repos?
3. ¿Qué interconexión vale más para los usuarios hoy? (Mi apuesta: **C**, pendientes de registrar en el Corella.)
4. ¿Existe una relación conocida entre código LMUC y material del PMIB (punto F)?
