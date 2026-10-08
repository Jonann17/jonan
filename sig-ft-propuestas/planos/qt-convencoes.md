# Convenções para migrar uma tela CustomTkinter → Qt (PySide6)

Leia antes de qualquer tarefa da migração Qt. Vale para implementadores e revisores.

## Repositório
- Repo `/home/user/sig-ft`, ramo `local/jonan-cambios` (ou a worktree que te deram). **SÓ LOCAL: nunca `git push`, nunca mexer em remotos.**
- Código, comentários e docs em português; mensagem de commit sem acento.
- Não editar `frontend.py` nem a interface CTk (`sigft/app/`), salvo pedido explícito da tarefa.
- Venv do repo: `/home/user/sig-ft/.venv/bin/python` (Python 3.13). Numa worktree, use esse mesmo python (ou `.venv` relativo ao repo principal).
- Commit termina com:
  ```
  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  Claude-Session: https://claude.ai/code/session_01RSbK7jX9qvsvyZKqnojmij
  ```

## Arquitetura Qt (já existe — reaproveite, não duplique)
- `sigft/app_qt/main.py` (janela, `TELAS` = registro nome→fábrica), `catalogo.py` (menu/cards), `estilo.py` (QSS global, `cinza_tk`, `mono`, fontes), `interface.py` (`na_interface(func,*args)`: ÚNICO caminho de uma thread para um widget), `file_dialogs.py` (mesma API e memória de pastas de `sigft/app/file_dialogs.py`).
- `widgets/`: `module_frame.ModuleFrame` (título, conteúdo, console, `log`, `backend(nome)`, `iniciar_tarefa(alvo,*args,botao=)`, modo `embutida`/`console_externo`), `espera.DialogosDeEspera` (`pausar_e_esperar`, `perguntar_retry_excel`, `perguntar_sim_nao`, `pedir_texto`, `avisar` — seguros de chamar do worker), `dialogs.py` (PausaLogin, RetryLock, SelecaoComCaixasDialog), `pickers.py` (FilePickerRow, MultiFilePickerRow, FolderPickerRow), `blocos.py` (`cartao`, `rotulo`, `botao(altura= real, variante=, cor_texto=)`), `console.ConsoleFrame`.
- Telas prontas para copiar o estilo: `sigft/app_qt/views/translator.py`, `sigft/app_qt/views/apagar_lmr.py` (+ testes `tests/test_qt_tela_*.py`).
- Regra de ouro das threads: o worker NUNCA toca widget direto (nem `setEnabled`, nem `QMessageBox`); só `self.log`, os métodos de `DialogosDeEspera`, `iniciar_tarefa` e `interface.na_interface`. Serviço nunca importa Qt. Threads de teste `daemon=True`.
- Backend: `self.backend("nome_backend")` (avisa o motivo se não carregou) — no clique, antes de abrir diálogos.
- Comportamento: IGUAL à tela CTk (mesmos textos, mensagens, ordem, regras). Bug de thread da tela CTk se corrige; qualquer outra diferença deliberada vai no relatório com o porquê.

## Paridade visual ("igual de bonito") — requisito
- Cores do tema: `theme.COLORS[...]`; nomes de cinza do Tk via `estilo.cinza_tk(...)` ("gray" = #808080 no Tk 8.6, nunca escrever #BEBEBE). `theme.COR_TEXTO_APOIO`="gray", `COR_TEXTO_APOIO_CLARO`="gray70".
- O QSS global já imita o tema dark-blue: botão #1F538D/texto #DCE4EE, CTkEntry (QLineEdit 28 px), checkbox, combo (= CTkOptionMenu), abas, console gray20 sem borda, cartão #2B2B2B. Use `blocos` em vez de estilo local; se faltar algo que vale para várias telas, ponha no código compartilhado (e diga no relatório).
- `pack`/`grid` do Tk SOMAM o pady de vizinhos: reproduza com `setSpacing(0)` + `addSpacing(soma)` comentando a origem (veja translator.py).
- `blocos.cartao` não centraliza o layout: centralize widgets de largura fixa com `alignment=AlignHCenter`.
- Compare em captura REAL (Xvfb) e meça com PIL (posições, tamanhos, cores). Iterar até diferença de poucos px (diferença de fonte é aceitável; relate o que sobrar).
  ```
  VENV=/tmp/claude-0/-home-user/111ccf73-6723-5e3b-a4c3-03916583ae47/scratchpad/venv312/bin/python   # 3.12 com tkinter + PySide6
  CAP=/tmp/claude-0/-home-user/111ccf73-6723-5e3b-a4c3-03916583ae47/scratchpad/capturas
  cd <repo ou worktree> && PYTHONPATH=$PWD timeout 120 xvfb-run -a -s "-screen 0 1400x900x24" $VENV <script> <saida> ...
  ```
  CTk: `$CAP/capturar_ctk.py <saida> <NomeDaTela>` (leia o script). Qt: modelo em `/tmp/claude-0/-home-user/111ccf73-6723-5e3b-a4c3-03916583ae47/scratchpad/capturar_qt_translator.py` (registra a tela em `TELAS` só dentro do script). Janela 1280x850. Salve as capturas finais em `$CAP/<tarefa>/`.
  Para diálogos/pop-ups: capture os dois lados também (abra-os no script).

## Testes e verificação (antes do commit, os dois)
- TDD: teste primeiro, ver falhar, implementar. pytest-qt offscreen; fixtures `qt_interface`/`qapp`/`qtbot` (veja `tests/test_qt_tela_translator.py`). Inclua o módulo novo no teste `test_qt_sem_tkinter` (grep).
- Um teste de geometria contra as medidas do CTk, como `test_medidas_iguais_as_do_customtkinter`.
- `bash scripts/check.sh` (tem de terminar "TUDO OK") **e** `/home/user/sig-ft/.venv/bin/ruff check .` (o CI roda). Saída de teste limpa.
- Um commit local por tarefa, só com os seus arquivos.

## Relatório
Escreva o relatório completo no arquivo indicado (o que fez, evidência TDD RED/GREEN, contagem de testes, ruff, tabela de medidas CTk×Qt, diferenças restantes, desvios deliberados com o porquê, arquivos, preocupações). Responda com SÓ (≤15 linhas): Status (DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT), commit(s) SHA + assunto, uma linha de testes, preocupações, caminho do relatório. Um único relatório final.
