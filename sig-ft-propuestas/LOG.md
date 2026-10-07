# Propuestas de cambios para SIG-FT

Repo original: https://github.com/luanccozer/SIG-FT (owner: luanccozer)

- Base: rama `claude/checkpoint-01-refactor-executor-5lawtu`, commit `1b7474c` (2026-10-07)
- Rama de trabajo local: `local/jonan-cambios`
- Estado de la base: 5337 tests pasan, 25 omitidos (`pytest -q`, Python 3.13, Linux)

Nada de esto se publica en el repo del owner hasta que decidamos enviarlo.
Cada cambio se guarda también como parche en `patches/` (se aplica con `git am`).

## Cambios

<!-- Plantilla por entrada:
### N. Título corto
- Fecha:
- Archivos:
- Qué cambia:
- Por qué:
- Cómo se probó:
- Parche: patches/000N-....patch
-->

_(todavía sin cambios aplicados al código de SIG-FT)_

## Borradores en revisión

- `specs/2026-10-07-migracao-qt6-design.md` — diseño de la migración de la interfaz
  de CustomTkinter a Qt6 (PySide6), autorizada por Luan. Pendiente de aprobación de
  Jonathan antes de entrar a SIG-FT (irá a `docs/superpowers/specs/`).
