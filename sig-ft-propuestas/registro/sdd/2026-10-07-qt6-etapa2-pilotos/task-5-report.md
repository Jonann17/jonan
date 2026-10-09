# Task 5 - Tela "Tradutor Tecnico" (Qt)

## Implementacao
- `sigft/app_qt/views/translator.py`: `ModuloTranslator` conforme o brief. Dois ajustes visuais sobre o codigo do brief,
  achados na captura: (1) o rotulo de descricao agora usa `setWordWrap(False)` (as 3 linhas ja vem quebradas; com quebra
  automatica dentro do cartao centralizado o texto aparecia cortado em ~1 linha); (2) os 3 botoes sao adicionados com
  `alignment=AlignHCenter` (sem isso ficavam encostados a esquerda da coluna, o original CTk centraliza cada um).
- `tests/test_qt_tela_translator.py`: exatamente os 5 testes do brief.
- `tests/test_qt_sem_tkinter.py`: `sigft.app_qt.views.translator` na lista.

## RED / GREEN
- RED: ImportError (`cannot import name 'translator'`) na coleta.
- GREEN: 15 passed (5 da tela + 10 do teste sem-tk), 5 execucoes seguidas (10 contando antes/depois dos ajustes visuais), todas verdes.

## Captura
/tmp/claude-0/-home-user/111ccf73-6723-5e3b-a4c3-03916583ae47/scratchpad/capturas/task5/qt_translator.png
(script: scratchpad/capturar_translator_qt.py). A tela CustomTkinter nao foi capturada.

## ruff / check.sh
- `ruff check .`: All checks passed.
- `scripts/check.sh`: 5527 passed, 25 skipped, TUDO OK.

## Concerns
- Console aparece vazio na captura porque o `ConsoleFrame` descarrega por QTimer (esperado).
- `blocos.rotulo` com `setWordWrap(True)` dentro de `cartao` (alinhamento HCenter) corta texto de varias linhas; as proximas telas
  com rotulos multilinha podem precisar do mesmo contorno (ou o fix pertence a `blocos`/`cartao`).
