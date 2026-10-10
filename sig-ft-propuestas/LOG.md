# Propuestas de cambios para SIG-FT

Repo original: https://github.com/luanccozer/SIG-FT (owner: luanccozer)

- Base: rama `claude/checkpoint-01-refactor-executor-5lawtu`, commit `3395788` (2026-10-07)
- Rama de trabajo local: `local/jonan-cambios`
- Estado de la base: 5337 tests pasan, 25 omitidos (`pytest -q`, Python 3.13, Linux)

Nada de esto se publica en el repo del owner hasta que decidamos enviarlo.
Cada etapa se guarda como parches en `patches/` (se aplican con `git am`).

## Cómo aplicar (para Luan)

```bash
git checkout claude/checkpoint-01-refactor-executor-5lawtu   # en 3395788 o más nuevo
git am /ruta/a/sig-ft-propuestas/patches/etapa1/*.patch
pip install -r requirements-dev.txt          # trae PySide6-Essentials y pytest-qt
bash scripts/check.sh                        # debe terminar en "TUDO OK"
python -m sigft.app_qt.main                  # interfaz Qt nueva (python frontend.py sigue igual)
```

En Linux, el Qt necesita estas bibliotecas del sistema (el CI ya las instala):
`sudo apt-get install -y libegl1 libxkbcommon0 libfontconfig1 libgl1`.

## Cambios

### 1. Qt6 — Etapa 1 (base de la interfaz nueva)
- **Fecha:** 2026-10-07
- **Parches:** `patches/etapa1/` (26 commits; el primero solo agrega el documento de diseño).
- **Diseño:** `specs/2026-10-07-migracao-qt6-design.md` (también va dentro del parche 0001).
- **Plan y registro:** `planos/2026-10-07-qt6-etapa1-base.md` y
  `planos/2026-10-07-qt6-etapa1-registro.md` (cada tarea, revisiones y decisiones).
- **Qué cambia:**
  - Paquete nuevo `sigft/app_qt/` (PySide6): splash, ventana principal con barra
    lateral, Home con los 12 cards. Las pantallas que todavía no se migraron
    muestran un aviso. Se abre con `python -m sigft.app_qt.main`.
  - Base para las próximas etapas: `estilo.py` (paleta de `theme.py`, fuentes Roboto
    y Noto Emoji, íconos en blanco y negro), `interface.na_interface` (único camino
    de un hilo a un widget), consola en lote, diálogos de espera, `ModuleFrame`.
  - **La interfaz actual (CustomTkinter) sigue siendo la oficial y no cambia de
    comportamiento.** `requirements.txt` queda igual; PySide6 está en
    `requirements-qt.txt` (incluido en `requirements-dev.txt`). El `.exe` no
    empaqueta Qt hasta el corte (`SIG-FT.spec` lo excluye, con test).
- **Arreglos que ya valen para la app actual:**
  - `frontend.py` verifica Python ≥ 3.10 y lo explica (antes, con 3.9, abría a medias
    con "unsupported operand type(s) for |").
  - `sigft/app/backends.py` guarda el motivo de cada módulo que no cargó
    (`falhas`, `exigir()`), en vez de fallar después con `'NoneType'`.
  - Textos de diálogos en `sigft/app/textos_dialogos.py` (sin tkinter);
    `sigft/app/widgets/dialogs.py` los re-exporta igual que antes.
  - `scripts/check.sh` ya no compila `.venv/`/`venv/` dentro del repo.
- **Bugs de la revisión inicial que la interfaz Qt ya resuelve por diseño:**
  ventanas creadas fuera del hilo de la interfaz (en macOS cierra la app), doble
  clic que lanza dos robots, módulo que no carga e impide abrir la app.
- **Por qué:** migración autorizada por Luan; optimización y la misma apariencia
  (aprobada por Jonathan con el prototipo `specs/prototipo/`).
- **Cómo se probó:**
  - `bash scripts/check.sh`: 5481 passed, 25 skipped (antes: 5337); `ruff check .` limpio.
  - App Qt abierta de verdad (Xvfb): `specs/prototipo/etapa1_app_qt_home.png` y
    `etapa1_app_qt_nao_migrada.png`. `frontend.py` (CustomTkinter) también abre igual.
  - Cada una de las 11 tareas de código pasó revisión independiente; revisión final
    de toda la etapa con 9 correcciones, verificadas.
  - Prueba en macOS por Jonathan: **pendiente** (la primera intención no llegó a aplicar
    los parches; ver instrucciones de "Cómo aplicar").
  - No se probó: PyInstaller/`.exe` en Windows (el CI de Release lo hará), ni el portal.
- **Medición** (`--smoke`, Xvfb, 3 corridas, mismos módulos cargados):
  CustomTkinter ≈ 3,75 s · Qt ≈ 3,34 s → ~0,4 s más rápido, **sin contar** los ~1,9 s
  de esperas artificiales que se quitaron de la splash en la apertura normal.
- **Nota para Rafael:** esta etapa **no toca** AutoSpec (ni `sigft/services/autospec*`
  ni su pantalla). Su pantalla se migra en la etapa 5, con una nota aparte.

### 2. Qt6 — Etapas 2 a 5 (en curso; pausado el 2026-10-09, retomado el 2026-10-10)
- **Retomado el 2026-10-10:** entraron la corrección de los uploads (revisada), la
  pantalla AutoSpec y la Home completa (`etapas3a6-en-curso/0017` a `0019`), las
  correcciones de Cria Fichas y de AutoSpec (`0020`, `0021`) y el corte: `python
  frontend.py` y `SIG-FT.bat` abren la interfaz Qt, `--ctk` abre la anterior, y hay
  lanzador para macOS (`0022`), y las segundas correcciones de la Home y de Cria
  Fichas (`0023`, `0024`). Siguen el `.exe` con Qt, el pulido y la revisión final.
  Este apartado se actualiza completo al terminar.
- **Parches:** `patches/etapa2-en-curso/` (14) y después `patches/etapas3a6-en-curso/`
  (24), en ese orden, encima de `patches/etapa1/`. Lo terminado pero sin integrar y lo
  que quedó a medias está en `patches/pendiente/` (ver su README).
- **Ya funciona en `python -m sigft.app_qt.main`, desde el menú y sin script:** Home
  (cards), Cria Fichas, Planilhas PMIB (PDM), Analyzer, Upload Condições, Tradutor,
  Upload Specs, Fichas Duplicadas, Aplicação LMR (Upload + Exclusão), PMIB Manager,
  Busca PMIB y el aviso de actualización al abrir. Correção de PDM está portada pero
  sigue bloqueada en el menú, igual que hoy.
- **Falta:** AutoSpec (a medias), paneles de la Home (claves, modelos y gastos de IA,
  mural, "Procurar atualizações", "Versões de teste"), revisión de Cria Fichas,
  integrar `pendiente/0001`, pulido visual compartido, corte (`frontend.py` y
  `SIG-FT.bat` abriendo Qt, `requirements.txt`, lanzador para macOS, `.exe`),
  revisión final de toda la rama y entrega.
- **Diferencias intencionales con la app actual (para que Luan decida):**
  - Confirmaciones destructivas (Apagar LMR, "Confirmar" de Correção de PDM): Enter
    elige "Não" (en Tk elegía "Sim").
  - Los avisos de fin ("Processo concluído") no frenan al robot: el navegador se
    cierra sin esperar el OK.
  - Cancelar el diálogo de carpeta ya no borra la ruta ya elegida (PMIB Manager, PDM).
  - Esc, Enter y Espacio no cierran ni confirman ventanas con trabajo de la persona
    (pesos del Analyzer, revisión de PDM, pausa de login, Excel bloqueado).
  - Un segundo clic trae al frente la ventana ya abierta en vez de abrir otra.
  - Los robots corren en hilo común: cerrar la ventana con un robot andando pregunta
    antes (regla del mural del 2026-09-25).
  - Si un módulo no cargó, el clic avisa el motivo en vez de fallar dentro del hilo.
- **Errores de la app actual que la versión Qt ya no tiene:** ventanas abiertas desde
  hilos de fondo (en macOS cierran la app), botones que quedaban trabados después de
  un error (Apagar LMR, LMR, Correção de PDM, Upload de Condições), pesos del Analyzer
  guardados a medias cuando un campo era inválido.
- **Cómo se probó:** `bash scripts/check.sh` → 6119 passed, 27 skipped; `ruff check .`
  limpio. Cada pantalla se comparó con la CustomTkinter en capturas reales (Xvfb)
  medidas con PIL: posiciones y tamaños iguales o a pocos px, casi todo por ancho de
  texto (la negrita larga sale hasta ~9% más ancha; pendiente de pulido). Cada tarea
  pasó por revisión independiente. **No probado:** portal real (RPA), `.exe` en
  Windows, macOS.
- **Nota para Rafael:** AutoSpec todavía no está migrada; no se tocó ningún archivo de
  su frente (`sigft/services/autospec*`, `sigft/core/web/`, `tests/test_autospec_*`).
- **Registro del proceso** (planos, briefs, informes de cada tarea y de cada revisión,
  scripts de captura): `registro/`.

## Hallazgos fuera de alcance (para Luan)

- `tests/test_llm_comparacao.py:408` hace `os.chdir(tmp_path)` sin restaurarlo
  (debería ser `monkeypatch.chdir`): los tests que usan rutas relativas al
  directorio actual fallan según el orden en que corren.

## Próximas etapas

Ver "Falta" en la sección 2. El plan completo está en
`planos/2026-10-08-qt6-etapas3a6-app-completa.md`.
