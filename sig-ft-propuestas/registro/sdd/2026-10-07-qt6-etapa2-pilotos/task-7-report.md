# Task 7: relatório. Tela "Automação LMR" (aba Upload) em Qt

**Status:** DONE_WITH_CONCERNS (as ressalvas são pequenas; ver o fim)
**Commit:** `9b0da5f` Qt6: aba de upload de aplicacoes LMR (local, branch `local/jonan-cambios`, sem push)

## O que foi feito

### A tela: `sigft/app_qt/views/lmr.py`

`ModuloLMR(parent=None, controller=None, *, embutida=False, console_externo=None)` expõe `.btn_run`, `.picker_status`, `.caixa_linha_inicial` (um QCheckBox), `.entry_linha_inicial`, `.caminho_status_pmib`, `_linha_inicial_escolhida()`, `escolher_aba()` e `escolher_pmibs()`.

- **Layout.** Segue o `pack` do CTk como `translator.py`/`apagar_lmr.py`: o cartão tem espaçamento 0 e cada `addSpacing` é a SOMA dos pady vizinhos (10, 20, 6, 30, 14, 8, 20), com 20 nas pontas. Cada espaço tem um comentário apontando a origem.
- **Centralização.** O seletor e o botão entram centrados com `AlignHCenter`. A linha "interruptor + 10 + campo de 70" fica centrada entre dois `stretch`.
- **Cores.** `cinza_tk(COR_TEXTO_APOIO / _CLARO)`. Não há `#BEBEBE` nem folha local no campo, que usa o QLineEdit global.
- **"Começar de um código específico".** No CTk, isto é um **CTkSwitch**, não uma caixa de marcar. Aqui é `controles.Interruptor`, uma subclasse de QCheckBox desenhada como o CTkSwitch: trilho de 36x18 (miolo de 30x12), botão redondo de 18, 6 px de vão, altura 24, `progress_color` = accent e fonte 12.
- **Comportamento.** Igual ao do CTk, com os mesmos textos e a mesma ordem:
  1. Excel (`lmr.excel`) → `listar_abas`. Se der erro: "Não consegui ler as abas do arquivo:\n{e}". Se não houver aba: "O arquivo não tem nenhuma aba.".
  2. Escolha da aba → "Lendo {arquivo} (aba '{aba}')...".
  3. Pré-processamento numa tarefa. As falhas são "Falha ao ler Excel:\n{msg}" (`avisar` com tipo erro), "Nenhum PMIB encontrado." e "Erro Pré-processamento: {e}".
  4. Seleção das fichas. Se vier vazia: "Seleção cancelada.".
  5. "{n} fichas selecionadas. Iniciando robô..." e o worker: "Iniciando navegador...", "Carregando portal...", `pausar_e_esperar(MSG_LOGIN_LMR)`, `processar_lista(..., callback_log=self.log, callback_ask=self.perguntar_sim_nao, callback_input=self.pedir_texto, linha_inicio=...)` e "Automação LMR finalizada.".
  6. `_marcar_status_do_lote`, com as mesmas mensagens `[i]`/`[!]`, seguido de `avisar("Sucesso", "Processo concluído.")`. Uma exceção grava "Erro Fatal LMR: {e}". `fechar_driver()` roda sempre.
- **`escolher_aba`.** É um `DialogoDaAba` igual ao CTkToplevel de 420x220: nome do arquivo em 12 negrito, pergunta em 12 gray70, `MenuDeOpcoes` de 300, "Ler esta aba" (primário) e "Cancelar" (#3A3A3A/#454545). Não usei `QInputDialog`, porque ele não se parece com a janela de lá.
- **`escolher_pmibs`.** É `SelecaoComCaixasDialog`. Fechar no "X" devolve `[]`.
- **Limpeza.** Os dois diálogos recebem `deleteLater()` depois do uso. Sem isso, cada clique deixava uma janela filha escondida.

### Peças compartilhadas, que valem para as próximas telas

- **`sigft/app_qt/widgets/controles.py` (novo).**
  - `Interruptor`: o CTkSwitch. Mais 5 telas CTk usam CTkSwitch: upload_tech_specs, upload_conditions, correcao_pdm (2) e copia_fichas.
  - `MenuDeOpcoes`: o CTkOptionMenu, com a parte escura da seta (#14375E, hover #1E2C40) e um "v" de 9x5 px com traço de 2. As medidas vêm da captura: no Windows e no Linux o CTk desenha a seta com a fonte de formas, não com o polígono.
  - `pintar_caixa`: a CTkCheckBox de 24 px, com borda 3 #949A9F, cantos 6 e o "v" gray90.
- **`dialogs.SelecaoComCaixasDialog` (Task 3) refeito para ficar com a cara da janela CTk.**
  - Rótulo de 14 em negrito, gray84.
  - Quadro `#quadro_caixas` gray13 com cantos 6, em (10, 53) com 430x494.
  - Cada linha é pintada por `_DelegadoDaCaixa` como uma CTkCheckBox: 28 px por linha e caixa 2 px abaixo do topo. Clicar na caixa ou no texto alterna; o resto da linha não alterna.
  - Barra de rolagem como a do CTkScrollbar: 16 px, alça gray41 de 8 px.
  - "Todos" 80x28 e "CONFIRMAR" 150x28 nas posições do CTk.
  - Continua sendo um QListWidget, a mesma API, e os testes antigos continuam passando.
- **`estilo.py`.**
  - **Indicador do QCheckBox: 20 → 18 px.** Medido: com 20 a caixa saía com **26 px**; a CTkCheckBox tem 24, porque no QSS width/height não contam a borda. Isso afeta a caixa "Versões de teste" da Home.
  - QComboBox com 28 px de altura e fonte 13, e lista com o DropdownMenu do tema (gray20/gray84/gray28).
  - Variante de botão "cinza" (#3A3A3A, hover #454545, o que as telas CTk escreviam à mão). "neutro" continua com o hover dele para a Home.
  - Regras `#quadro_caixas`/`#lista_caixas`, com notas no bloco de comentários.
- **`tests/conftest.py`.** Hook `pytest_runtest_teardown` (hookwrapper) que roda `gc.collect()` depois de cada teste que usa `qtbot`. Ver "Segfault" abaixo.

## Segfault encontrado e corrigido (systematic-debugging)

`pytest tests/test_qt_tela_lmr.py tests/test_qt_controles.py tests/test_qt_perguntas.py -q` morria **sempre** com segfault em `Interruptor.paintEvent`. Com `-v` ou com só um arquivo, não morria. O backtrace nativo (gdb) apontou `QPainter::setFont → QPainter::device()`.

- **Hipótese 1** (ler `self.font()` no meio da pintura): **rejeitada**. A falha continuou e só mudou de lugar, para `QPainter(self)`.
- **Hipótese 2** (GC fora de hora): **confirmada**. Com `gc.disable()` não morre, e com `gc.collect()` depois de cada teste também não.

O mecanismo:
1. O pytest-qt fecha as telas com `close()` + `deleteLater()`, mas o `processEvents()` dele não roda o DeferredDelete. O C++ continua vivo e dono do Python.
2. A tela é lixo em ciclo: o seletor guarda `self._ao_escolher_status`, que guarda a tela.
3. O GC a apaga quando quer, no meio da pintura do teste seguinte.

Em produção as telas ficam referenciadas, então o problema é de higiene dos testes. O `test_qt_tela_apagar_lmr` tinha o mesmo ciclo latente. A correção ficou no conftest e vale para todo teste Qt.

## TDD

- **Controles.** RED: `ImportError: cannot import name 'controles'`.
  - O indicador, conferido à parte: com 20 → `assert (26, 26) == (24, 24)`; com 18 → passa.
  - O menu: `assert (30 == 28)` antes de ajustar a regra do QComboBox.
  - GREEN: 5 passed.
- **Diálogo de seleção.** RED: o teste novo de medidas e da cara falhou, enquanto os 5 antigos passavam. GREEN: 6 passed.
- **Tela.** RED: `ImportError: cannot import name 'lmr' from 'sigft.app_qt.views'`. GREEN: 21 passed.
  - O que os 21 cobrem: textos e cores; caixa e campo; linha vazia e inválida; memória do seletor; fluxo completo, com a ordem do log, callbacks, `linha_inicio=7`, `retry_lock`/`callback_log` e o aviso.
  - Também: sem STATUS; falha na planilha; Erro Fatal; seleção vazia; cancelar aba; cancelar arquivo; falha ao ler; sem PMIB; erro no pré-processamento; sem abas; abas ilegíveis; backend indisponível (não abre o seletor); modo embutido.
  - E ainda: as duas escolhas com as janelas de verdade (incluindo "X" = nenhuma), as medidas da tela e as medidas da janela da aba.
- `test_qt_sem_tkinter` ganhou `views.lmr` e `widgets.controles`.
- Depois da correção do conftest, rodei 5 vezes os 4 arquivos com ordem aleatória: 45 passed nas 5. A suíte Qt inteira, 3 vezes: 170 passed. A saída com `-rw` está limpa.

## Verificação

- `bash scripts/check.sh`: **5596 passed, 25 skipped**, "TUDO OK (compileall + pytest)". Os 19 warnings já existiam.
- `.venv/bin/ruff check .`: **All checks passed!**

## Comparação visual (Xvfb, 1280x850, tela avulsa)

- **Scripts:** `$CAP/capturar_ctk_lmr.py` (tela CTk avulsa, a aba Upload dentro da seção "Aplicação LMR", interruptor ligado e os dois diálogos) e `scratchpad/capturar_qt_lmr.py`. Há cópias dos dois em `$CAP/task7/`.
- **Capturas e lado a lado:** em `$CAP/task7/` estão `lado_a_lado_lmr.png`, `lado_a_lado_lmr_ligado.png`, `lado_a_lado_aba.png` e `lado_a_lado_pmibs.png`. A referência de como o app mostra a tela é `ctk_aplicacao_lmr_upload.png`. A seção Qt é da Task 8.

y é contado a partir do topo do cartão.

| Peça | CTk | Qt | Δ |
|---|---|---|---|
| Cartão, em relação ao conteúdo / altura | +20 / 465 | +20 / 454 | 0 / -11 (rótulos de várias linhas) |
| Título: y / altura | 20 / 28 | 20 / 28 | 0 |
| Texto de 4 linhas (13 px): altura | 68 | 63 | -5 |
| Espaços título→texto→marcar→seletor | 10 / 20 / 6 | 10 / 20 / 6 | 0 |
| Seletor: botão / x / largura da linha | 240x28 / 512 / 533 | 240x28 / 513 / 530 | ≤3 |
| Botão: tamanho / x / espaço acima | 300x50 / 628 / 30 | 300x50 / 628 / 30 | 0 |
| Interruptor: x / largura / altura | 627 / 223 / 24 | 626 / 225 / 24 | ≤2 (largura do texto) |
| Campo: x / tamanho / interruptor em relação ao campo | 860 / 70x28 / +2 | 861 / 70x28 / +2 | ≤1 |
| Espaços botão→linha→explicação→script→fim | 14 / 8 / 20 / 20 | 14 / 8 / 20 / 20 | 0 |
| Explicação (11 px, 3 linhas) / script (12 px, 3 linhas): altura | 42 / 45 | 39 / 42 | -3 / -3 |
| Janela da aba: 420x220; rótulos y 20/52; menu e botões (60, 97/145/183) 300x28 | — | idêntico | 0 |
| Janela de fichas: 450x600; quadro (10,53) 430x494; 1ª linha (16,59) 28 px; barra x=423 w=16; Todos (10,562) 80x28; CONFIRMAR (290,562) 150x28 | — | idêntico | 0 |

**Cores.** Medidas no miolo da tinta e nos fundos, são iguais nas duas capturas:

| Peça | Cor |
|---|---|
| Fundo | #212121 |
| Cartão | #2B2B2B |
| Título | #00C975 |
| Texto | #808080 |
| Marcar | #E0E0E0 |
| Botão do seletor | #3A3A3A |
| Botão | #035D67, texto #FFFFFF |
| Explicação e script | #B3B3B3 |
| Campo | fundo #343638, borda #565B5E |
| Dica "0" (desabilitado) | #9E9E9E no CTk × #9D9D9D no Qt |
| Texto do interruptor | #D6D6D6 |
| Trilho do interruptor | #4A4D50, ligado #00C975 |
| Botão do interruptor | #D5D9DE |
| Seta do menu | parte escura #14375E |
| Caixa da seleção | borda #949A9F, marcada #035D67 |
| Quadro da seleção | #212121 |

## Diferenças que ficaram

1. **Rótulos de várias linhas ficam 1 px mais baixos por linha** (13 px: 16 contra 17). O cartão sai 11 px mais baixo, e as peças abaixo de cada texto sobem até 5 px.
   - A causa é a métrica: o Tk no Linux usa ceil(ascent hhea) + ceil(descent) (medido: 14/15/17 para 11/12/13 px). O Qt, com hinting completo, arredonda.
   - **Não forcei a altura do Tk-Linux:** no Windows, o GDI usa outras métricas (winAscent/winDescent), e copiar o número do Linux poderia piorar lá, onde as pessoas usam o app. É a mesma diferença "de fonte" que a Task 6 já aceitou, só que aqui há mais linhas.
2. **Larguras de texto** variam de 1 a 3 px (interruptor 225 contra 223; seletor 530 contra 533). Diferença de fonte.
3. **Hover:** a CTkCheckBox muda a cor ao passar o mouse, e a linha pintada pelo delegado não muda. O "v" da caixa é um traço, e o do CTk é um glifo da fonte de formas; as formas são quase iguais (comparei com zoom).
4. **A caixa "Versões de teste" da Home (QCheckBox global) continua sem o "v" quando marcada.** Sem imagem, o QSS não desenha a marca. Fica para uma tarefa da Home: usar `pintar_caixa` ou uma imagem.

## Desvios deliberados

- **O backend é verificado (`self.backend`) antes do seletor de arquivo.** O brief e o CTk só usavam o backend depois de escolher o arquivo, e no CTk um backend ausente morria com `AttributeError`. Segue a convenção "no clique, antes de abrir diálogos".
- **`_linha_inicial_escolhida()` roda na thread da interface** (`_na_interface_e_esperar`), lida no mesmo momento de lá, depois do login. O brief lia os widgets da thread do robô, o que a regra de ouro proíbe.
- **O diálogo da aba é uma janela própria, e não `QInputDialog.getItem`,** para ter a cara da janela CTk.
- **`SelecaoComCaixasDialog` ganhou o parâmetro opcional `cor_caixa`** (padrão primary, o da tela LMR).
- **Botão durante a seleção.** O botão volta a ficar habilitado entre o pré-processamento e o worker, enquanto a seleção modal está aberta: `iniciar_tarefa` devolve o botão ao fim do pré-processamento. Como a janela é modal, ninguém consegue clicar nele. No CTk ele ficava desabilitado o tempo todo.

## Arquivos

- `/home/user/sig-ft/sigft/app_qt/views/lmr.py` (novo)
- `/home/user/sig-ft/sigft/app_qt/widgets/controles.py` (novo)
- `/home/user/sig-ft/sigft/app_qt/widgets/dialogs.py` (SelecaoComCaixasDialog + `_DelegadoDaCaixa`)
- `/home/user/sig-ft/sigft/app_qt/estilo.py` (indicador 18, QComboBox, variante cinza, quadro e lista da seleção)
- `/home/user/sig-ft/tests/test_qt_tela_lmr.py`, `tests/test_qt_controles.py` (novos)
- `/home/user/sig-ft/tests/test_qt_perguntas.py` (+1 teste), `tests/test_qt_sem_tkinter.py` (+2 módulos), `tests/conftest.py` (gc depois de cada teste Qt)

## Ressalvas

- Mexi em peças compartilhadas: `estilo.py` (o indicador do QCheckBox muda a Home), `dialogs.py`, `conftest.py` e o `controles.py` novo. Tudo pela paridade ou pela estabilidade, e com testes.
- As diferenças 1 e 4 acima.
- A tela NÃO foi registrada em `main.py`, como pedia a tarefa (fica para a Task 8).

---

## Correção pós-revisão: o botão fica desligado da leitura até o fim do robô

**Commit:** `Qt6: LMR mantem o botao desligado da leitura ate o fim do robo`. Arquivos: `sigft/app_qt/views/lmr.py`, `tests/test_qt_tela_lmr.py` e `tests/conftest.py`.

**Defeito (Important).**
- O `_pre_processamento` rodava em `iniciar_tarefa(botao=btn_run)`.
- Ele enfileirava `_selecionar_e_rodar`, e o `finally` da tarefa enfileirava `_reabilitar(btn_run)` logo em seguida.
- Quando a seleção voltava rápido e a tarefa do robô começava primeiro, essa reabilitação atrasada religava o botão com o robô rodando.

**Correção.**
- `_pre_processamento` agora faz tudo em UMA tarefa: lê o Excel, chama `_escolher_pmibs_e_esperar` (a janela abre na thread da interface via `_na_interface_e_esperar` e a tarefa espera), registra no log e chama `_worker_lmr` na mesma tarefa.
- O botão desliga no clique de "Ler esta aba" e só volta no fim do robô, como no CTk.
- Um erro da janela de seleção volta como `("erro", e)`, é relançado e vira "Erro Pré-processamento: {e}". Antes ele se perdia no `interface._rodar`, só com traceback.
- O método `_selecionar_e_rodar` saiu, e o import de `interface` também.

**TDD.**
- RED, 3 de 3: `test_botao_fica_desligado_da_leitura_ate_o_fim_do_robo` (com `processar_lista` preso, `btn_run.isEnabled()` dava True) e `test_erro_na_janela_de_selecao_vira_log` falharam.
- GREEN: 23 passed, 5 de 5, em ordem aleatória.
- `_esperar_fim` deixou de ser vazio: ele afirma `not btn_run.isEnabled()` antes de esperar o botão voltar.

**Minor 1 (conftest).**
- O hook trocou `gc.collect()` por `QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)`, que é mais barato e determinístico.
- O segfault original não se reproduz mais, nem sem hook. Testei com o código atual e numa cópia exportada de `9b0da5f`, nas duas ordens: `apagar_lmr, lmr, controles` e `lmr, controles, perguntas`. Ele depende do layout de memória, então um A/B direto não prova nada.
- Por isso conferi o mecanismo:
  - depois de `close()` + `deleteLater()` + `processEvents()`, o que o pytest-qt faz, o C++ da tela continua **vivo**: `shiboken6.isValid` dá True, e esse é o risco;
  - depois do flush do DeferredDelete, o C++ está **morto** (False);
  - o GC posterior só recolhe cascas Python já invalidadas.
- Isso elimina a causa: um C++ apagado pelo GC em hora aleatória, no meio de uma pintura.

**Minor 2: diferenças deliberadas, que faltavam no relatório.**
- **"X" na janela de fichas:** agora grava "Seleção cancelada." e devolve o botão. No CTk, fechar no "X" não chamava `on_confirm`, e o botão ficava preso desligado.
- **"Processo concluído."** não bloqueia (`avisar`). No CTk, o `showinfo` segurava o worker, e o navegador ficava aberto até o OK.
- **Lista de fichas sem alternância pelo teclado:** a lista é `NoFocus`, e o delegado só responde ao mouse. No CTk dava para marcar uma caixa com Tab + Espaço.

**Verificação.**
- `bash scripts/check.sh`: TUDO OK (5700 passed, 26 skipped). O número inclui as mudanças em andamento da Task 8 nesta mesma cópia de trabalho.
- Suíte Qt: 256 passed, 3 de 3.
- `ruff check .`: All checks passed.
