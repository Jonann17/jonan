# Task 1 - Robustez + botoes em portugues

Status: DONE. Commit 5ebc911 "Qt6: robustez para as telas reais e dialogos do Qt em portugues".

## Implementacao (exatamente como no brief)
- interface.instalar(): RuntimeError fora da thread do QApplication / sem QApplication.
- console.log: no RuntimeError zera `_agendado` sob a trava.
- module_frame: `_reabilitar(botao)` engole RuntimeError de widget destruido.
- backends: `_modulo_de`, `exigir` levanta KeyError p/ nome desconhecido, mensagem "(módulo X)".
- nao_migrada: `TelaComErro` (atributo `mensagem`).
- main: `_instalar_traducao(app)` chamada em `_preparar_qt`; `show_frame` mostra TelaComErro sem cache.

## RED
`.venv/bin/python -m pytest tests/test_qt_robustez.py -q` -> 7 failed (as 7 esperadas).

## GREEN
Mesmo comando -> 7 passed. Com test_qt_interface, test_qt_main, test_backends_falhas, test_app_backends -> 43 passed.

## Traducao
`QApplication.translate("QPlatformTheme", "Cancel") == "Cancelar"` funcionou como no brief; nenhum ajuste de contexto necessario.

## Verificacao
- `.venv/bin/python -m ruff check .` -> All checks passed!
- `bash scripts/check.sh` -> 5488 passed, 25 skipped; TUDO OK.
- Nenhum teste existente precisou ser adaptado.

## Arquivos
sigft/app_qt/{interface.py,main.py,views/nao_migrada.py,widgets/console.py,widgets/module_frame.py}, sigft/app/backends.py, tests/test_qt_robustez.py (novo).

## Concerns
Nenhuma. Observacao: a unica chamada de `exigir` com nome fora de MODULOS agora levanta KeyError; nenhum teste/codigo existente dependia disso.
