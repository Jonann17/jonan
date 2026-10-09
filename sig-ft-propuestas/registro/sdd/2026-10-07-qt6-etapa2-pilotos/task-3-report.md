# Task 3 - relatorio

## Implementacao
- `espera.py`: em `DialogosDeEspera`, `_na_interface_e_esperar`, `perguntar_sim_nao`, `pedir_texto`, `avisar` (codigo do brief, verbatim). Imports `QInputDialog, QMessageBox`.
- `dialogs.py`: `SelecaoComCaixasDialog` (brief, verbatim); imports `QListWidget, QListWidgetItem`.
- `tests/test_qt_perguntas.py`: 5 testes do brief, verbatim (threads daemon=True).
- Metodos/classes existentes intactos.

## RED / GREEN
- RED: 5 failed (AttributeError: 'avisar'/'SelecaoComCaixasDialog' ausentes).
- GREEN: 5 passed.

## Estabilidade
5 execucoes seguidas: 5 passed em todas.

## ruff + check.sh
- ruff: All checks passed.
- check.sh: TUDO OK (compileall + pytest). tests/test_qt_sem_tkinter.py: 6 passed.

## Arquivos
sigft/app_qt/widgets/espera.py, sigft/app_qt/widgets/dialogs.py, tests/test_qt_perguntas.py

## Ressalvas
Nenhuma. Nota: `avisar` com `tipo` invalido levanta KeyError (como no brief).
