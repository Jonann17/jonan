# Task 8: seção "Aplicação LMR" + Tradutor/LMR no menu Qt: relatório

**Status:** DONE_WITH_CONCERNS (as ressalvas estão em "Preocupações")
**Commit:** `eda6b3d` Qt6: secao Aplicacao LMR com as duas abas e Tradutor/LMR no menu
(sobre `11e574b`, a correção da Task 7 que outro agente commitou durante esta task)

## O que foi feito

- **`sigft/app_qt/views/aplicacao_lmr.py`** (novo): `ModuloAplicacaoLMR(parent=None, controller=None)`,
  um `ModuleFrame` com título "Aplicação LMR" e `peso_conteudo=3`. Atributos: `.abas` (um
  `widgets.abas.Abas`), `.tela_upload` (`ModuloLMR`) e `.tela_exclusao` (`ModuloApagarLMR`).
  As duas telas entram embutidas (`embutida=True, console_externo=self.console`), cada uma em
  `abas.add("Upload de Aplicações" | "Exclusão de Aplicações")`. A seção abre sempre em Upload.
  - Mudança de rumo: o coordenador pediu `Abas` no lugar de `QTabWidget`, e eu troquei. **Não**
    mexi em QTabWidget no `estilo.py`. No `estilo.py` não houve mudança nenhuma.
  - Área rolável medida no CTk: a margem do layout de cada tela embutida é (6, 6, 17, 6). Os 6 vêm
    do canvas do CTkScrollableFrame, que fica a `corner_radius` da borda; o `Abas` já recua os
    outros 6 do Tabview. À direita entram 1 + 16 px da faixa da barra. Assim a área fica com os
    888 px de lá. A barra do Qt só aparece quando há o que rolar, a mesma decisão da barra lateral.
- **`sigft/app_qt/main.py`**: `TELAS` ganhou `"Translator"` → `ModuloTranslator` e `"LMR"` →
  `ModuloAplicacaoLMR`, com os imports.
- **Correções em widgets compartilhados (estritamente necessárias, só 2 trechos):**
  1. **`widgets/abas.py`, `Abas.add`**: `aba.setStyleSheet("background: transparent;")` não tinha
     seletor, então valia para TODOS os descendentes. O cartão (#2B2B2B) e os botões grandes
     ("Selecionar Excel e Iniciar", "INICIAR LIMPEZA") ficavam sem fundo, e a seção saía quebrada.
     Agora é `QWidget(objectName="aba_abas")` + `"#aba_abas { background: transparent; }"`
     (4 linhas). Regressão nova em `test_qt_controles_e31.py::test_abas_nao_apaga_o_fundo_do_que_vai_dentro`.
  2. **`widgets/module_frame.py`, ramo `embutida`**: o `QScrollArea.setWidget` liga o autoFill do
     conteúdo. Quando o defeito 1 parou de esconder isso, apareceu a paleta clara do Qt (#EFEFEF)
     atrás do cartão. Agora `self.content.setAutoFillBackground(False)` e o mesmo no viewport
     (5 linhas). Só esta seção usa o modo embutido.
- **Testes:** `tests/test_qt_tela_aplicacao_lmr.py` (4 testes) e o módulo novo em
  `test_qt_sem_tkinter.py`.

## TDD

- RED 1: `ModuleNotFoundError: sigft.app_qt.views.aplicacao_lmr`.
- RED 2, depois de trocar para `Abas`: `AttributeError: QTabWidget has no attribute 'abas'`.
- RED 3, defeito do `Abas`: `assert '#212121' == '#2B2B2B'`, o fundo do cartão sumia.
  Conferi também que, com o `abas.py` antigo (git stash), o teste da seção falha.
- RED 4, autoFill do QScrollArea: `assert '#EFEFEF' == '#212121'`.
- GREEN: os 4 da seção + os 10 do e31 + module_frame/main/sem_tkinter dão 54 passed, saída limpa.

## Verificação

- `bash scripts/check.sh`: **TUDO OK**, 5700 passed, 26 skipped. Os 19 warnings já existiam
  e nenhum vem dos testes novos.
- `ruff check .`: All checks passed!
- `python -m sigft.app_qt.main --smoke` (offscreen): "a janela principal Qt montou e fechou sem erro."
- **Abri o app de verdade sem script e sem registrar nada em TELAS** (Xvfb, `capturar_qt_secao.py`).
  Clique no card "Aplicação LMR" da Home → `ModuloAplicacaoLMR`. Clique em "Exclusão de
  Aplicações" → troca de aba. Clique no "4.2. Tradutor" da barra lateral → `ModuloTranslator`.
  Clique no "7. Aplicação LMR" da barra lateral → volta à mesma seção, já criada e na aba em que
  estava.
- Capturas em `$CAP/task8/`:
  - lado a lado: `lado_a_lado_{upload,exclusao,translator,home}.png` e os recortes `*_conteudo.png`;
  - CTk: `ctk_lmr_upload.png`, `ctk_lmr_exclusao.png`, `ctk_translator.png`, `ctk_home.png`;
  - Qt: `qt_lmr_upload.png`, `qt_lmr_exclusao.png`, `qt_translator.png`, `qt_home.png`;
  - scripts: `capturar_ctk_secao.py`, `capturar_qt_secao.py`, `sonda_ctk_filhos.py`, `sonda_qt_filhos.py`.

## Medidas CTk × Qt (janela 1280x850, coordenadas da janela)

| Peça | CTk | Qt |
|---|---|---|
| título | 317,30 h29 | 317,30 h29 |
| conteúdo (Tabview) | 317,79 923x571 | 317,79 923x571 |
| console | 317,670 923x150 | 317,670 923x150 |
| barra segmentada | 635,89 287x27 | 636,89 284x27 (centro 778,5 nos dois) |
| botão "Upload de Aplicações" | 137 | 136 |
| botão "Exclusão de Aplicações" | 150 | 148 |
| quadro do Tabview | gray13 = #212121 (some no fundo) | #212121 |
| área rolável (canvas / viewport) | 329,128 888x510 | 329,127 888x511 |
| cartão (Upload) | 329,148 888x465 | 329,147 888x454 |
| botão "Selecionar Excel e Iniciar" | 623,386 300x50 | 623,380 300x50 |
| cartão (Exclusão) | 329,148 888x428 | 329,147 888x418 |
| botão "INICIAR LIMPEZA" | 598,411 350x50 | 598,405 350x50 |
| cor do cartão / fundo da área | #2B2B2B / #212121 | #2B2B2B / #212121 |

A maior parte dos 6 px a menos no y dos botões vem da altura dos rótulos de várias linhas. A
entrelinha do Tk é maior: "Este módulo…" 68 × 63, "irreversível" 34 × 31, "O robô irá" 75 × 70.
É a mesma diferença de fonte já aceita nas Tasks 6/7. Os espaços entre as peças são iguais. Mais
1 px vem do `Abas` (ver Preocupações).

## Diferenças restantes

- Junção dos botões segmentados: por desenho do `Abas`, idêntica ao CTk no zoom
  (`zoom_abas_ctk_qt.png`). Larguras -1/-2 px por fonte.
- Barra de rolagem: no CTk é um traço de 16 px sempre visível. No Qt fica a faixa vazia, e a barra
  global de 10 px aparece só quando falta altura, por dentro dos 888. Desvio deliberado, igual à
  barra lateral.
- O "INICIAR LIMPEZA" sai mais escuro na captura do CTk (#B71C1C) porque o ponteiro do Xvfb, em
  (700,450), está em cima dele: é o hover. No Qt o botão está em #D32F2F, a cor normal. Não é
  defeito.

## Preocupações / para o merge

1. **`Abas` fica 1 px acima do CTk no conteúdo da aba (y 42 × 43).** A barra visível tem 27 px, e
   no Tk ela alarga a linha 2 da grade do CTkTabview para 19. Correção sugerida em
   `widgets/abas.py`: `setRowMinimumHeight(2, ALTURA_BARRA_VISIVEL - SOBRA_DA_BARRA)` e a margem
   de cima do conteúdo `ALTURA_BARRA_VISIVEL - SOBRA_DA_BARRA + CANTO` (25). Não apliquei, porque
   não é estritamente necessário e o widget é da outra frente. Meu teste de geometria tolera ±1 só
   nesse eixo, com comentário.
2. **`blocos.area_rolavel` tem o mesmo defeito do item 1 das correções.** `interno.setStyleSheet("background: transparent;")`
   sem seletor (e o do viewport também). Todo cartão ou botão dentro dessa área perde o fundo. Não
   mexi (fora do escopo). A correção é a mesma: `objectName` + seletor.
3. Mexi em 2 arquivos de `widgets/` (`abas.py` e `module_frame.py`), descritos acima, para a merge
   com a frente dos widgets. O `estilo.py` não mudou.
4. Outro agente commitou a correção da Task 7 (`11e574b`: `views/lmr.py`, `conftest.py`,
   `test_qt_tela_lmr.py`) neste checkout durante a task. Meu commit não toca nesses arquivos, e a
   suíte verde já inclui a mudança dele.

## Arquivos

- Novos: `sigft/app_qt/views/aplicacao_lmr.py`, `tests/test_qt_tela_aplicacao_lmr.py`
- Alterados: `sigft/app_qt/main.py`, `sigft/app_qt/widgets/abas.py`, `sigft/app_qt/widgets/module_frame.py`,
  `tests/test_qt_controles_e31.py`, `tests/test_qt_sem_tkinter.py`
