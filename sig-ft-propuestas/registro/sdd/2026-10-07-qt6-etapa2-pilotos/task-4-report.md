# Task 4 - relatorio

Status: DONE

## Implementacao
Criados, exatamente como no brief: `sigft/app_qt/file_dialogs.py`, `sigft/app_qt/widgets/pickers.py`, `sigft/app_qt/widgets/blocos.py`.
Testes: `tests/test_qt_file_dialogs.py`, `tests/test_qt_pickers.py`; os tres modulos novos foram incluidos na lista de `tests/test_qt_sem_tkinter.py`.

## RED / GREEN
RED: ImportError (`cannot import name 'pickers'`), 2 erros de coleta.
GREEN: 17 passed (file_dialogs + pickers + sem_tkinter).

## Verificacao
ruff check .: All checks passed. scripts/check.sh: 5518 passed, 25 skipped, TUDO OK.

## Concerns
Nenhum. `sigft/app/file_dialogs.py` e `pickers.py` (CTk) intocados.
