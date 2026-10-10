### Spec Compliance
- ✅ **Spec compliant.** Everything in E5.1 is present and matches the CTk Home. Two narrow divergences are listed under Minor #1 and Important #1.
  - **Bar:** same order, CTk colours, 40 px tall, Roboto 13 bold, the theme hover #14375E, mono icons (sigft/app_qt/views/home.py:59-65, 373-419). "Atualizações" calls `atualizacao.procurar_agora(controller)`. Its `ao_terminar` runs on the UI thread (sigft/app_qt/atualizacao.py:137-145) and is guarded with `isValid` (home.py:421-432).
  - **"Versões de teste":** a `CaixaDeMarcar` at size 12. Its value is set before `toggled` is connected, so building the screen does not write the preference. An unreadable preference shows as unchecked (home.py:395-405).
  - **Cards:** CTk's `criar_card_instrucao` is dead code; a grep finds only its own definition, at sigft/app/views/home.py:1111. So the "instruction cards" are the module cards. Their texts are identical to CTk's `MODULOS` (checked by AST).
  - **Panels:** chaves (home.py:608-662), modelos (665-1114), gastos (1120-1162) and mural (486-584 plus widgets/mural.py), each in a `JanelaPainel`.
  - **Texts:** I collected every user-facing string literal by AST. Every CTk string in `home.py` and `mural.py` appears verbatim in the Qt files. The only exceptions are the dead `📥 ENTRADAS`/`📤 SAÍDAS` labels.
  - **Logic, function by function:** provider preselected by majority, "(salvo)" entries, filter never drops the current choice, manual > list > default, remount in place, save loops over all tasks. All identical.
  - **Coordinator's question (compact cards with the new bar):** the approved design is kept.
    - The description uses the full card width: a 408 px label in a 438 px card, with no 380 px wrap.
    - In `capturas/e5.1/qt_Home.txt` the last card ends at y 789. Content height is 789+6+20 = 815, which is ≤ 850.
    - The bar row ends at x 928, inside the 946 px content edge.
    - `test_medidas_da_home` (tests/test_qt_home_paineis.py:951-979) asserts both scroll bars have maximum 0.
    - `lado_a_lado_Home.png` shows all 12 cards with no scrolling.
    - The 438 px width, the positions and the header colours (gray84) are the CTk-measured values, as "Espaçamento igual ao de hoje" asks.
  - **Global constraints:**
    - Threads: the worker gets a copy of the keys and comes back only through `na_interface`, with an `isValid` guard and `try/finally` (home.py:962-987).
    - Keyboard: every button, check box and menu is NoFocus, and the panels are QWidget windows. Enter, Esc and Space neither save nor close (tests :338, :574, :618).
    - A second click raises the open window (home.py:435-457; test :279).
    - "Aplicar mesmo assim?" defaults to No (home.py:1074).
    - `mono` is used only on fixed emoji labels, never on keys or model ids.
- ⚠️ **Cannot verify from the diff:**
  - The real catalog fetch, opening the logs folder in Explorer and the GitHub check were exercised only with doubles.
  - Windows only:
    - The 12-card fit has 35 px of slack. One extra wrapped line in three different rows would make the Home scroll.
    - The 15 px line height for Roboto 12 was measured on Linux.
    - `activateWindow()` raising an already-open panel depends on Windows foreground rules.

### Strengths
- The parity work is thorough:
  - Texts are locked against the CTk source by AST (`keys_info`, `rotulos_tarefa`).
  - The mural tables have an equality test.
  - Each panel has a geometry test against `winfo_*` measurements, plus real captures. Panel positions match CTk to ±1 px.
- Thread bug fixed properly: daemon thread, copy of the keys, return only through `na_interface`, discard if the panel was destroyed, and the label cannot stay stuck on "Buscando...".
- The earlier review lessons are all applied and tested: one panel per type that a second click raises, no key auto-confirms or discards, destructive question defaults to Não.
- Tests save the model selection for real, in the isolated `api_config.json`; only the network and the usage log are doubled. The wheel and focus tests were shown failing (RED) first.
- Shared-code changes are minimal and listed in the report. The card-title fix (`addStretch`) corrects a Stage-1 defect and comes with its own test.
- Rich text is handled safely in the Home: `_Texto` uses PlainText, or RichText with `html.escape` (home.py:160, 170-176).

### Issues
#### Critical (Must Fix)
None.

#### Important (Should Fix)
1. **Data-access logic copied line for line into the Qt view, with no test keeping the two copies in sync.**
   - **What:** `HomeView._ler_mural` and `_caminho_do_mapeamento` (sigft/app_qt/views/home.py:496-584) are line-for-line copies of sigft/app/views/home.py:216-316, about 85 lines.
   - **Why it matters:**
     - The block contains no widget code: openpyxl reading, column mapping, a prefs fallback and `os.listdir`.
     - It is exactly the block with a history of real bugs: `ws.cell` taking 3.9 s, `data_inicio` read as blank, FAIXAS listed by hand.
     - The report and summary say tests check both sides stay identical. That is true only for the mural tables (`test_desenho_do_mural_igual_ao_customtkinter`, tests/test_qt_home_paineis.py:185) and a few text constants (:172).
     - The shared checks in tests/test_mural_nomes_do_servico.py:57/80/147 only lock invariants: service names exist, the FAIXAS one-liner is present, no `ws.cell`. A new column, or a fix to the path fallback, made on one side breaks no test.
     - At the cut, the CTk copy disappears and this logic stays in a Qt view. That goes against CLAUDE.md principle 2 (no business rules in the UI).
     - The migration already has a pattern for this: `sigft/app/textos_dialogos.py` (7356884) and `sigft/app/atualizacao_textos.py` (e3ade01) are tkinter-free modules that the CTk side re-exports.
   - **Fix:**
     - Move both functions somewhere tkinter-free, for example `sigft/services/atividades.py` as `ler_mural_do_mapeamento(hoje) -> (gavetas, erro)` and `caminho_do_mapeamento()`.
     - Call them from the Qt Home, and have the CTk methods delegate to them, as `atualizacao.py` does.
     - Point the `iter_rows` and FAIXAS checks at the service.
   - **Fallback:** if you keep "copy until the cut" (the precedent is pmib_manager's `_texto_dos_avisos`), at minimum add an AST-dump equality test for the two functions and correct the report's claim.

#### Minor (Nice to Have)
1. **The mural renders spreadsheet text as HTML.**
   - `mural._rotulo` builds `QLabel(texto)` with the default `AutoText` format (sigft/app_qt/widgets/mural.py:91). It is used for user data: the group (:211-213), the description (:218), and the "com …/status" line (:236-245).
   - Checked offscreen on an archive of HEAD: `"Trocar <a> por <b> no PDM"` lays out 112 px wide because the tags are swallowed. A `&lt;` on the first line would also switch the label to rich text. CTk shows the text verbatim.
   - Fix: add `r.setTextFormat(Qt.TextFormat.PlainText)` in `_rotulo`, plus a test.
2. **Test gaps on the deliberate deviations.**
   - The `mensagens` fixture ignores the buttons and default arguments (tests/test_qt_home_paineis.py:82-96), so the "Não" default (deviation #5) is not locked.
   - `test_catalogo_que_chega_depois_do_painel_destruido_e_descartado` (:680-695) waits 50 ms and checks only that no traceback appeared. It never checks that the guard actually ran; a spy on `_recarregar_modelos_do_provider` would make it decisive.
   - The minimized-window restore path is untested.
3. **Restore un-maximizes.** `_trazer_para_frente` calls `showNormal()` (home.py:441), which un-maximizes a panel that was maximized and then minimized. `setWindowState(windowState() & ~Qt.WindowState.WindowMinimized)` restores it without losing the maximized state.
4. **File size and a small duplicate.** `views/home.py` is already 1162 lines (Home, three panels, mural reading, local helpers). `_rotulo` is nearly duplicated in home.py:126 and mural.py:84; it could be one helper in `blocos`. Not blocking, since the structure mirrors CTk and that eases the cut.
5. **Shared-code changes, for awareness:**
   - `MenuDeOpcoes.wheelEvent` (controles.py:113-118) now also affects Busca PMIB (busca_pmib.py:291) and LMR (lmr.py:49). It matches CTk, whose CTkOptionMenu ignores the wheel, and no test relied on wheel changes.
   - The always-visible scroll bar and the no-focus "Fechar" (painel_janela.py:61-72, 83) affect only the Home, its sole user.
   - The 19 warnings in the reported run are pre-existing openpyxl warnings from test_autorizados.py, test_painel.py and test_pmib_manager_v2.py. None come from this task.

### Assessment
**Task quality:** Needs fixes

**Reasoning:** The port is faithful and well tested: texts, logic, geometry, threads and the approved compact cards all check out. The one blocking item is the unsynchronized line-for-line copy of `_ler_mural`/`_caminho_do_mapeamento` into the Qt view, which departs from the migration's shared-module pattern and makes the report's "kept identical" claim false. Extracting it (or at least adding an identity test), plus the one-line PlainText fix for the mural, clears it.
