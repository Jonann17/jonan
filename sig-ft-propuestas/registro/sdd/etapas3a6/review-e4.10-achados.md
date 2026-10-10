### Spec Compliance
- ❌ **Issues found.** The port is complete: all texts, messages, dialog keys and the order of rules match `sigft/app/views/autospec.py` line by line. It is registered as a lazy factory (`main.py` `_autospec` plus `TELAS["AutoSpec"]`), and the conferência block came over with its three outside dependencies (`autospec.py:37`, `:47`, `:384`). Two binding requirements are not met:
  - **Behaviour differs from CTk on user data, and the difference is not reported.** A link title containing "&" is shown altered (`autospec.py:471`). See Important #1.
  - **The "a button cannot re-enable mid-chain" rule is broken for PROCESSAR** (`autospec.py:434`, reached from `:543` and `:736`). See Important #2.
  - **The report's deviation #2 describes the CTk behaviour wrongly** (`e4.10-report.md:182-186`, `:297-299`). See Minor #2.
- ⚠️ **Cannot verify from the diff:**
  - **No real run yet.** The real `AutoSpecCore`, IA and web were never run (the report says so). This needs a run on a machine with the keys.
  - **Possible conflict in `cria_fichas.py`.** This task edits `cria_fichas.py:76-79`, and that file is also being changed by the E4.9 fix round (`progress.md:27`). Watch for a conflict when cherry-picking that fix.

### Strengths
- **Thread discipline is right.** The workers only use `self.log`, `self.avisar` and `interface.na_interface`.
  - The queue copy, `_STATUS_PMIB` and the supplier checkbox are read on the click (`autospec.py:687-688`). The 2nd pass also takes the conferência and the selection on the click (`:577-578`).
  - `_novo_core` is still the only place that builds the core (`:693`).
  - Checked: `controller.get_key` only reads a dict (`main.py:281-282`), so the worker touches no widget.
- **The CTk invariants are proven by running the screen, not by AST.** "Show before save" is checked with a real `.txt` round-trip (`tests/test_qt_tela_autospec.py:417`), and "the section never hides" at `:476`.
- **`mono` is applied only to the fixed emoji.** User data is tested unaltered (`:275`, `:450`).
- **The shared-code changes are minimal and backward-compatible.** `pintar_caixa(..., lado=LADO_CAIXA)` has a default, and `lado` is keyword-only in `CaixaDeMarcar`. Checked the callers: `dialogs.py:186`, `pmib_manager.py:109/281`, `cria_fichas.py:227` and `cria_fichas.py:87` (which imports `estilo` at `:27`).
- **Visual parity is very close.**
  - Variant colours match the CTk hovers (`estilo.py:204-224`).
  - I viewed `lado_a_lado_conferencia.png` and `lado_a_lado_com_fila.png`; they are nearly identical.
  - The geometry tests are thorough.
- **No file of Rafael's is touched** (diff stat). The registration test now mounts AutoSpec in the real app (`test_qt_registro_telas.py:44-49`).
- **The +1 skip (27→28) is by design.** It is the new `FORA_DO_RECORTE` entry (`tests/test_texto_da_ui.py:117-118`), not noise.

### Issues

#### Critical (Must Fix)
None.

#### Important (Should Fix)

**1. `sigft/app_qt/views/autospec.py:471` — a web-page title is put into a QPushButton without escaping "&".**
- **What happens:** Qt treats "&" as a mnemonic marker. The "&" is not drawn ("R&S" shows as "RS", "Products & Solutions" loses the "&"), and the button grabs an Alt shortcut that opens the browser.
- **Measured** with a scratch script against this screen:
  - the title `"Products & Solutions | R&S"` gives `link.shortcut() == 'Alt+Space'`, which is the Windows system-menu chord;
  - button `sizeHint` widths: "R&S" = "RS" = 133 px, but "R&&S" = 141 px.
- **Why it matters:** the CTk button showed the title literally. The title is what the person reads to judge the document. This is the same "never alter user data" class as the earlier `mono` finding.
- **Fix:** use `titulo.replace("&", "&&")` in the button text only, and add a test with a "&" title (assert `link.shortcut().isEmpty()`).

**2. PROCESSAR re-enables while a 2nd pass is still running (`autospec.py:434`).**
- **What happens:** `_conferencia_mostrar` does `btn_conf.setEnabled(bool(conferencia))` unconditionally. It is called by IMPORTAR (`:543`), which is always enabled, and by the end of a batch (`:736`).
- **Reproduced** in a scratch script: during a held 2nd pass PROCESSAR was disabled; after IMPORTAR it was enabled; a second click started a second concurrent pass (2 cores created).
- **Why it matters:** `processar_conferidos` rewrites each ficha's `_completed` file (`services/autospec.py:3780-3782`). Overlapping passes race on those writes. Re-importing the same `.txt` mid-pass and clicking again is a plausible accident.
- **Related:** at the end of a pass, `_reabilitar` (`module_frame.py:30-35`, `:150-152`) re-enables PROCESSAR even when the list has meanwhile become the empty state.
- This is inherited from CTk (`sigft/app/views/autospec.py:242`, `:381`), but it breaks a binding constraint. The same class was fixed in E4.45 ("um robo por vez").
- **Fix:**
  - keep a flag such as `_conf_em_andamento`, set on the click;
  - in `_conferencia_mostrar`, use `setEnabled(estado and not flag)`;
  - at the end, post a callback that clears the flag and sets `btn_conf.setEnabled(bool(self.conferencia))`, instead of passing `botao=` to `iniciar_tarefa`;
  - add one test.

#### Minor (Nice to Have)
1. **`autospec.py:725-739` — an error at the end of a batch is no longer reported in the console.** In CTk, an exception while showing the list ended up as "ERRO FATAL: …" in the console, with no "Sucesso". Now `_fila_processada` runs in the bridge, which only prints a traceback to stderr (`interface.py:28-31`), and the worker then shows "Sucesso" anyway (`:721`). Fix: wrap the body in a try that logs `ERRO FATAL: {e}`.
2. **The report's description of the old queue behaviour is wrong.**
   - CTk's `process_queue` walks the live `self.queue` (`services/autospec.py:3919`, `for i, task in enumerate(queue)`). So items added during a batch were processed in that same batch. Only items added after the loop ended were wiped, for example while the CTk "Sucesso" box was open, since it came before `self.queue = []` (`sigft/app/views/autospec.py:468-473`).
   - Now items added mid-batch wait for the next run. That is a user-visible change presented as a pure fix.
   - Correct deviation #2 (`e4.10-report.md:182-186`), Nota item 1 (`:297-299`) and the test comment at `tests/test_qt_tela_autospec.py:357-359`.
3. **The always-on scroll-bar stylesheet block is now copied verbatim in three files:** `autospec.py:118-121`, `copia_fichas.py:87-90`, `cria_fichas.py:131-134`. This is already deferred to the polish task (`progress.md:35`).
4. **`autospec.py:736` — inherited product behaviour, for the Nota or PENDENCIAS.** A batch ending replaces an imported conferência that has unsaved marks (or empties it), and those marks are lost. CTk does the same (`sigft/app/views/autospec.py:477`).
5. **`tests/test_qt_tela_autospec.py:757`, `:763` — fixed `qtbot.wait(50)` sleeps** before geometry asserts may be flaky under load. Use `waitUntil` on the expected position.
6. **No test covers an "X" clicked during a batch**, although the report claims it no longer affects the running batch. Coverage gap.
7. **Space presses whichever button has focus.** CTk buttons never took focus. This is already tracked for all screens (`progress.md:36`). Checked: after clicking an "X", focus goes to the console, so Space does not remove another item.
8. **Nits:**
   - `controles.py:178` still says "A caixa de 24", but the size is now a parameter.
   - `cria_fichas.py:79` keeps an alias that only `:87` uses.
   - The `font-family` append is repeated at `autospec.py:288-289` and `cria_fichas.py:87`.

### Assessment
**Task quality:** Needs fixes

**Reasoning:** The port is faithful, thread-safe in its workers and visually very close, and the tests prove behaviour by running the screen. Two small fixes are needed first: link titles with "&" are displayed altered and grab Alt shortcuts, and PROCESSAR can be re-enabled mid-pass, which allows concurrent 2nd passes on the same fichas.

