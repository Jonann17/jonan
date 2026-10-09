# Task 6: relatório. Tela "Apagar Aplicações LMR" (aba Exclusão) em Qt

**Status:** DONE_WITH_CONCERNS (as ressalvas são pequenas e ficam fora do escopo; ver o fim)
**Commit:** `df1f610` Qt6: aba de exclusao de aplicacoes LMR (local, branch `local/jonan-cambios`, sem push)

## O que foi implementado

- `sigft/app_qt/views/apagar_lmr.py`: `ModuloApagarLMR(parent=None, controller=None, *, embutida=False, console_externo=None)`, com `.entry_pmib`, `.picker_status`, `.btn_run`, `.caminho_status`.
  - O layout segue o `pack` do CTk como no `translator.py`: o cartão tem espaçamento 0, e o `addSpacing` vale a SOMA dos pady vizinhos (5, 30, 25, 5, 30, 20), com margens de 20 e um comentário apontando a origem de cada espaço.
  - A linha do PMIB fica centrada: rótulo de 14 px em negrito sem quebra de linha, 20 px de espaço (os padx 10 + 10) e campo de 250x28. O campo tem a folha própria: altura 28 com borda, fonte 13 e `placeholder-text-color` gray62, iguais ao CTkEntry do tema dark-blue.
  - O seletor e o botão "INICIAR LIMPEZA" (350x50, `perigo`, 14 px em negrito, texto `text_white`) entram centrados com `AlignHCenter`.
  - Cores: `cinza_tk(COR_TEXTO_APOIO)` para "gray" e `cinza_tk(COR_TEXTO_APOIO_CLARO)` para gray70. Nenhum `#BEBEBE` literal.
  - Comportamento, na mesma ordem do CTk:
    1. PMIB vazio: `QMessageBox.warning("Aviso", "Digite o código PMIB.")`;
    2. confirmação "Tem certeza que deseja APAGAR todas as aplicações do PMIB {pmib}?";
    3. "Preparando limpeza para: {pmib}..."; o worker escreve "Iniciando navegador...", "Carregando portal...", depois `pausar_e_esperar(MSG_LOGIN_APAGAR_LMR, texto_botao=TEXTO_COMECAR_EXCLUSAO)`, "Iniciando varredura...", `executar_limpeza(pmib, callback_log=self.log)` e "Processo Finalizado.";
    4. `_limpar_status_do_lote` com as mesmas regras e textos: sem planilha não faz nada; `limpou=False` grava a linha `[i]` e não mexe na planilha; erro vira a linha `[!]` sem derrubar o resultado; o recado sai com 3 espaços na frente;
    5. `avisar("Sucesso", "Limpeza concluída.")`; uma exceção grava "Erro Fatal: {e}"; `fechar_driver()` roda sempre, no `finally`.
  - O botão é desabilitado e devolvido por `iniciar_tarefa`, que usa uma thread comum, como manda o `instancia.encerrar`.
- **Desvio consciente do brief:** o backend é verificado com `self.backend(...)` em `iniciar_limpeza`, ANTES da confirmação, e o módulo é passado ao worker. O brief verificava dentro do worker. O motivo é o mesmo padrão do Translator ("backend que não carregou não abre diálogo"): não faz sentido perguntar "tem certeza?" para depois dizer que o módulo não carregou. No CTk, esse caso morria com `AttributeError` dentro da thread.
- `sigft/app_qt/widgets/pickers.py`: o seletor Qt era a primeira peça usada de verdade e destoava do CTk em duas coisas, corrigidas na peça compartilhada (hoje só esta tela a usa):
  - `setSpacing(0)` mais 15 px dos DOIS lados do rótulo. Antes eram 6 + 15 de um lado só, e a linha centrada saía deslocada.
  - O rótulo de status passou a ter 13 px, a fonte padrão do CTkLabel; antes usava a fonte do app. O texto "Nenhum (…)" media 201 px de largura contra 216 no CTk; agora mede 218 contra 216.
- `tests/test_qt_sem_tkinter.py`: `sigft.app_qt.views.apagar_lmr` entrou na lista.

## TDD

RED da tela:
```
$ .venv/bin/python -m pytest tests/test_qt_tela_apagar_lmr.py -q
E   ImportError: cannot import name 'apagar_lmr' from 'sigft.app_qt.views'
1 error in 0.19s
```
GREEN da tela: `12 passed`. Rodei 5 vezes (com `test_qt_sem_tkinter`): `23 passed` nas 5.

RED do seletor (teste novo `test_medidas_iguais_as_do_customtkinter` em `tests/test_qt_pickers.py`):
```
E       AssertionError: assert 'font-size: 13px' in 'color: #808080; background: transparent;'
1 failed, 4 passed
```
GREEN: `5 passed`.

Testes da tela (12): textos e cor do título; memória de pastas do seletor (chave, categoria, título, filetypes e log); PMIB vazio; "Não" na confirmação; backend indisponível não pergunta; fluxo completo com STATUS (ordem das linhas, `retry_lock`/`callback_log`, pausa com a mensagem e o botão certos); sem STATUS; limpeza incompleta; falha na planilha; erro no portal (Erro Fatal, driver fechado, sem aviso); modo embutido no console do pai; medidas iguais às do CTk. Nenhum teste cria thread própria.

## Verificação

- `bash scripts/check.sh`: **5554 passed, 25 skipped**, "TUDO OK (compileall + pytest)". Os 19 warnings já existiam; os testes novos não geram nenhum (`-rw` limpo).
- `.venv/bin/ruff check .`: **All checks passed!**

## Comparação visual (Xvfb, 1280x850, tela avulsa)

Scripts: `$CAP/capturar_ctk_apagar_lmr.py` (registra a tela CTk avulsa em `app.frames`) e `scratchpad/capturar_qt_apagar_lmr.py` (registra em `TELAS` só dentro do script). As capturas finais estão em `$CAP/task6/ctk_apagar_lmr.png` e `qt_apagar_lmr.png`. A montagem lado a lado está em `scratchpad/lado_a_lado_task6.png`.

Na tabela, y é contado a partir do topo do cartão; nas medidas horizontais, a posição é relativa ao centro do cartão.

| Peça | CTk | Qt | Δ |
|---|---|---|---|
| Cartão, em relação ao conteúdo | +20 | +20 | 0 |
| Cartão, altura | 428 | 426 | -2 (rótulo de 2 linhas: 34 vs 32) |
| ATENÇÃO, y / h | 20 / 28 | 20 / 28 | 0 |
| Irreversível, y / h | 53 / 34 | 53 / 32 | 0 / -2 (métrica da fonte) |
| Linha PMIB, y | 117 | 115 | -2 (herdado de cima) |
| Campo PMIB | 250x28 | 250x28 | 0; a tinta cai exatamente nos mesmos px dentro do cartão |
| Opcional, h | 30 | 30 | 0 |
| Seletor: botão / x do botão | 220x28 / -234.5 | 220x28 / -235 | ≤1 |
| Seletor: vão botão→texto | 17 | 17 | 0 |
| INICIAR LIMPEZA | 350x50, centro -1 | 350x50, centro -0.5 | ≤1 |
| Passos, h / centro | 75 / -0.5 | 75 / -0.5 | 0 |
| Espaços entre as peças | 5/30/25/5/30/20/20 | 5/30/25/5/30/20/20 | 0 |

As cores no núcleo do texto e nos fundos são idênticas: título e ATENÇÃO `#D32F2F`; irreversível e rótulo do seletor `#808080`; opcional e passos `#B3B3B3`; placeholder `#9E9E9E`; campo `#343638` com borda `#565B5E`; botão do seletor `#3A3A3A`; botão `#D32F2F` com texto `#FFFFFF`; cartão `#2B2B2B`; fundo `#212121`.

## Diferenças visuais que ficaram

1. **O texto em negrito sai uns 10% mais estreito no Qt** (ATENÇÃO: 221 vs 237 px; INICIAR LIMPEZA: 109 vs 121; "Código PMIB:": 86 vs 94). Por isso a linha do PMIB fica 3–4 px deslocada. A causa é a fonte: o app registra só Roboto Regular e Medium, e o mesmo acontece no Tradutor. Fica fora desta tarefa.
2. **O texto de 2 linhas e 13 px ocupa 32 px no Qt e 34 no CTk**, e tudo abaixo dele sobe 2 px. É métrica de fonte, dentro da tolerância.
3. **O texto do botão do seletor é `#E0E0E0` no Qt e `#DCE4EE` no CTk.** A causa é global: o `QPushButton` em `estilo.py` usa `text_light`, enquanto o CTkButton do tema dark-blue usa `#DCE4EE` por padrão. Isso vale para TODO botão sem cor própria, inclusive o `contorno_padrao` do Tradutor. Não mexi, porque é folha global e afeta outras telas. Sugestão: tarefa própria para trocar a cor padrão do `QPushButton`, e talvez a do `contorno_padrao`, por `#DCE4EE`.
4. **O conteúdo começa em x=310 e tem 930 de largura no Qt; no CTk, x=317 e 923.** Vem da barra lateral do app (`main.py`), não desta tela.

## Arquivos

- `/home/user/sig-ft/sigft/app_qt/views/apagar_lmr.py` (novo)
- `/home/user/sig-ft/tests/test_qt_tela_apagar_lmr.py` (novo)
- `/home/user/sig-ft/sigft/app_qt/widgets/pickers.py` (espaçamento e fonte do rótulo)
- `/home/user/sig-ft/tests/test_qt_pickers.py` (+1 teste de medidas)
- `/home/user/sig-ft/tests/test_qt_sem_tkinter.py` (+1 módulo)

## Ressalvas

- `pickers.py` é peça compartilhada da Task 4. A mudança só alinha a peça ao CTk e, hoje, só esta tela a usa.
- O desvio da verificação do backend descrito acima.
- As diferenças 3 e 4 merecem tarefas próprias, fora daqui.
