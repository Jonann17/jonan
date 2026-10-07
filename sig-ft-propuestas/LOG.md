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
  - No se probó: PyInstaller/`.exe` en Windows (el CI de Release lo hará), ni el portal.
- **Medición** (`--smoke`, Xvfb, 3 corridas, mismos módulos cargados):
  CustomTkinter ≈ 3,75 s · Qt ≈ 3,34 s → ~0,4 s más rápido, **sin contar** los ~1,9 s
  de esperas artificiales que se quitaron de la splash en la apertura normal.
- **Nota para Rafael:** esta etapa **no toca** AutoSpec (ni `sigft/services/autospec*`
  ni su pantalla). Su pantalla se migra en la etapa 5, con una nota aparte.

## Hallazgos fuera de alcance (para Luan)

- `tests/test_llm_comparacao.py:408` hace `os.chdir(tmp_path)` sin restaurarlo
  (debería ser `monkeypatch.chdir`): los tests que usan rutas relativas al
  directorio actual fallan según el orden en que corren.

## Próximas etapas

2. Selectores de archivo + pantallas piloto ApagarLMR y Translator.
3. LMR, BuscaPMIB, PMIBManager, Analyzer, PDM.
4. UploadConditions, UploadTechSpecs, CopiaFichas, CorrecaoPDM (bloqueada).
5. CriaFichas y AutoSpec (con nota para Rafael).
6. Paneles de la Home, actualización automática, `.exe` con Qt y corte de `frontend.py`.
