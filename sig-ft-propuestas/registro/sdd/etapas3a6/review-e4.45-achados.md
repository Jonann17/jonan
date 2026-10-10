
I made no changes to the repo. The branch tip moved to a37d43c (Correção de PDM) while I was reviewing, but none of the reviewed files changed after e3fa0f1.

**Tests I ran:**
- **Focused tests:** 230 passed, 1 skipped. They were run with `.venv/bin/python -m pytest` over the two new screen test files, `test_qt_dialogos_de_acao_medidas`, `test_qt_espera`, `test_qt_sem_tkinter`, `test_qt_tela_copia_fichas`, `test_qt_tela_lmr`, `test_qt_tela_apagar_lmr`, `test_qt_dialogos_selecao`, `test_app_dialogos_da_tela` and `test_app_dialogs`.
- **Lint:** `ruff` and `pyflakes` are clean on the changed files.

### Spec Compliance
- **Same behaviour as CTk (risk a):** I compared both screens line by line with `sigft/app/views/upload_conditions.py` and `upload_tech_specs.py`. All of these match: titles, config texts and margins, switch text, tab names, FileQueueList keys/labels/filetypes, which list actions get logged (Conditions logs only "adicionou"; Tech Specs logs all three), warning texts and their order, PARAR confirmations and logs, the save flows, and the selection-dialog arguments.
  - The two web-start rules are kept: Conditions demands `_STATUS_PMIB` in `_pre_start_web`, and Tech Specs only logs the "Aviso: … NÃO serão marcadas" line.
  - Tech Specs still goes straight to `_start_web_process` after saving; Conditions goes through `_pre_start_web`.
  - Pause messages are right: Conditions uses `MSG_LOGIN_SOLTAR_ROBO`/`msg_falha_ao_salvar`, Tech Specs uses `MSG_LOGIN_SOLTAR_ROBO`/`msg_ficha_preenchida`. `ask_callback` uses the default `MSG_EXCEL_BLOQUEADO`, as in CTk.
  - Nothing from one screen leaks into the other through the shared base `TelaDeUpload`: the differences live in class attributes and subclass methods.
- **Thread safety (risk b):** workers only use `log`, `pausar_e_esperar`, `perguntar_retry_excel`, `avisar` and `interface.na_interface`. The switch and `caminho_status` are read on the UI thread and passed in as arguments. The pause and Excel-lock dialogs open from the worker through `DialogosDeEspera`. Robot threads are not daemon threads, so closing the window asks first.
- **Dialog consolidation (risk c):** the constructor signatures of `PausaLoginDialog` and `RetryLockDialog` did not change. The only callers are in `espera.py`; LMR, Apagar LMR and Cópia de Fichas reach them through `pausar_e_esperar`, and those tests pass. The kept Cópia measurement test passes. Enter now does nothing in the pause, Excel-lock and locked-files dialogs, and the three new tests cover it.
- **Deviations (risk d):** all four are implemented as reported: backend checked on click, Tech Specs controller created on first click, PARAR switched off in `finally` after an error, and the Conditions robot created inside the `try` with a guarded `fechar()`.
- **Review lessons (risk e):**
  - `mono` is not used anywhere.
  - Button colours on the screens are right: `cor_fundo` is used where CTk had only `fg_color`, and `variante` where CTk had a matching hover.
  - The selection dialog is ApplicationModal, so it cannot open twice.
  - "One `iniciar_tarefa` per chain" holds: the IA task's late re-enable only touches `btn_ia` and the IA PARAR, never the web buttons, and CTk also re-enabled `btn_ia` when IA finished.
- `main.py`, `catalogo.py`, `frontend.py` and `sigft/app/` are untouched. The new modules are in `test_qt_sem_tkinter`.

### Strengths
- The base class is a clean merge of the two near-twin screens, and the pack/pady sums are commented next to their CTk source.
- The tests check exact console lines, which dialogs were asked in which order, and which thread the pauses came from.
- The geometry tests are deterministic because they call `carregar_fontes`.
- `ler_resultados_excel` is pulled out and tested with real pandas.
- The Enter fix in the shared dialogs is backed by tests that fail on the old code.
- I spot-checked the side-by-side captures (Tech Specs tab 1 with a full list, Excel-lock dialog); they match closely.

### Issues

**Critical:** none.

**Important**
1. **A JSON file with the wrong shape now fails silently** (`sigft/app_qt/views/upload_tech_specs.py:220-226`).
   - **What:** `_pre_start_web(dados)` was moved out of the `try`. In CTk (`upload_tech_specs.py:322-327`) it was inside, so a JSON whose top level is a dict, or whose items aren't dicts, logged "Erro ao ler JSON: 'str' object has no attribute 'get'".
   - **Evidence:** I ran it offscreen. With `{"METADATA": …}`, clicking "Carregar JSON" leaves the console empty, and the `AttributeError` only reaches `sys.excepthook` (stderr). The person sees nothing happen.
   - **Why it matters:** the deviation is not in the report and it falls under risk (a). Conditions (`upload_conditions.py:249-256`) has the same restructuring; there it is harmless in practice, since `to_dict("records")` always gives dicts, but it still differs from CTk.
   - **Fix:** put `self._pre_start_web(dados)` back inside the `try` on both screens, as in CTk, and add a test with a dict-shaped JSON that expects the "Erro ao ler JSON" line.

**Minor**
2. **"Tentar Novamente" has the wrong hover colour** (`sigft/app_qt/widgets/dialogs.py:127`). It uses `variante="primario"`, so the hover is `primary_hover` #047A83. In CTk (`sigft/app/widgets/dialogs.py:155-162`) it has `fg_color=primary` and no `hover_color`, so the hover is the theme's #14375E. The line was rewritten in this task under "medidas do CTk". Fix: `blocos.botao("Tentar Novamente", cor_fundo=theme.COLORS["primary"], largura=150, altura=40)`.
3. **The "grow to fit the text" button logic is duplicated** (`_upload_comum.py:33-45` `botao_que_cresce`, and `dialogs.py:93-99`). `blocos.botao(largura_minima=...)` already does this and is used by `pdm.py` and `janelas.py`. I measured both: `largura_minima=200` gives 212 for INICIAR, and `largura_minima=estilo.LARGURA_BOTAO_CTK` gives 201 for the pause button, the same as the copies. Fix: use `blocos.botao(..., largura_minima=)` in both places and drop the copies (`pmib_manager._botao_ctk` is a third copy, for the polish list).
4. **Space still releases the pause and decides the Excel-lock dialog** (`dialogs.py:100-103`, `127-131`). I checked offscreen: focus lands on the button when the dialog opens, and Space releases the pause. The stated reason for the Enter fix ("no CTk nenhuma tecla estava ligada"; a stray key releases the robot before login) applies to Space just as much, because CTkButtons never take focus. Fix: `setFocusPolicy(Qt.FocusPolicy.NoFocus)` on these buttons, plus a Space key in `_apertar_enter`. Esc releasing the dialog is the earlier decision from 952522a and is out of scope.
5. **Deviation 4 has no test** (`upload_conditions.py:274-307`). Two tests are missing: one where `UploadAutomation()` raises, and one where `fechar()` raises. Each should check that "Erro Crítico Web" is logged and that the web buttons and PARAR come back.
6. **`_marcar_escolhido` keeps appending to the stylesheet** on every pick (`_upload_comum.py:202-208`). This is the same known polish item listed for pdm and pmib_manager; add `_upload_comum` to it in `progress.md`.
7. **Two robots can run at once** (optional, same as CTk). `_on_ia_finished`, then "Continuar", calls `_pre_start_web`/`_start_web_process` without checking whether a robot is already running. This can only happen if the person started one from a file while the IA ran. In Tech Specs that would mean two `executar_pipeline_rpa` calls on the same controller. A guard on `btn_parar_web.isEnabled()` or `automacao_ativa` would close it; otherwise note it in PENDENCIAS.
8. **Stale test comment** (nit, `tests/test_qt_tela_copia_fichas.py:435`). It says "texto + 6 de cada lado", but the code now uses `FOLGA_TEXTO_BOTAO_CTK` = 7.

### Assessment
**Needs fixes.** Only item 1 blocks, and it is a one-line move plus one test. Items 2–5 are small and worth doing in the same fix commit; items 6–8 can go to the ledger.

