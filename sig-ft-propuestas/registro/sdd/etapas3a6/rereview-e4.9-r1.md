### Finding Verdicts

Line numbers are from 4530a3a. `cria_fichas.py` and its tests are byte-identical at the checkout HEAD (ab74059). Experiments ran on `git archive` copies in `/tmp/claude-0/-home-user/111ccf73-6723-5e3b-a4c3-03916583ae47/scratchpad/rev49fix/` (`head/tests/test_rev_e49fix.py`, `base/tests/test_rev_base_b.py`, `headfix/`). The checkout is still clean.

1. **Important #1 (AI worker read screen state live)** — ADDRESSED.
   - `cria_fichas.py:461-462` take `df` and `caminho_pdm` at the click. `:469-470` pass them, plus the key, as arguments.
   - `_ai_worker` (`:472-550`) reads only its arguments and `self.log`. No `df_data_selecionado`, `file_path_pdm`, `catalogo` or `df_processed` appears inside it.
   - Check run, on the exact scenario of the finding: block INSIDE `processar_lote`, then `pos_selecao([2,3])`.
     - Base 748d3a4 gives `[('C','PDM.1111.001 - A'),('D','PDM.1111.002 - B')]`, the bug.
     - Head gives `[('A','PDM.1111.001 - A'),('B','PDM.1111.002 - B')]`.
   - Test nit, not blocking: `tests/test_qt_tela_cria_fichas.py:511` parks the worker in the categorizer constructor, one step earlier than the finding asked.
     - It catches live reads of the path and df given to `carregar` and `processar_lote`.
     - It would not catch a regression of the `df.iloc[i]` read after `processar_lote` returns. The code has no such read now.

2. **Minor #2 (failure opening the review locked "3. Analisar")** — ADDRESSED.
   - `:562-570`: `abrir_revisao_pdm` is in try/except. On failure it calls `traceback.print_exc()`, logs, and calls `_fim_da_cadeia_da_ia()`.
   - `:559-561`: a `None` result also ends the chain.
   - Test at `:552` checks the log, the button, the flag, the progress bar and stderr.
   - Residual, not the finding: `_parar_progresso()` at `:558` sits outside the try and catches only `RuntimeError`.

3. **Minor #3 (closed `JanelaResumo` windows piled up)** — ADDRESSED.
   - `:834-838` set `WA_DeleteOnClose`.
   - Check run with the real `JanelaResumo`:
     - **Close paths:** the Fechar button, a new batch (`janela.close()` on the open one) and Esc each leave `findChildren(JanelaResumo) == []` after DeferredDelete.
     - **Stale reference:** `isVisible()` raises `RuntimeError`, which `:824-827` handles.
     - **Leaks:** `dialogos_selecao._ABERTOS` goes back to 0, so no Python reference leaks.
   - Test at `:806` uses the real class.

4. **Minor #4 (four labels with the wrong gray)** — ADDRESSED.
   - `:71` defaults `cor` to `controles.COR_TEXTO_CTK`, which is #D6D6D6.
   - The four labels (`:218, 228, 319, 328`) pass no `cor`. Every other `_rotulo` caller (`:84, 234, 254, 334`) passes one explicitly.
   - Rendered on #2B2B2B with the global stylesheet, the brightest red channel is 214 on all four labels. The review measured 224 before.
   - Test at `:230` asserts the stylesheet.

5. **Minor #5 (edição "Concluído" box no longer waited)** — ADDRESSED.
   - `:1024` calls `avisar(..., esperar=True)` inside the try, before the `finally` that quits the driver (`:1028-1032`).
   - Test at `:978` asserts `{"esperar": True}` and that the browser has not quit when the box is called.
   - The test replaces `avisar`, so the wait itself rests on the existing `esperar=True` coverage in `test_qt_espera`.

6. **#6a (robot could run unreviewed data)** — ADDRESSED.
   - **`df_processed` writers:** `__init__` (`:167`), `:606` and `resetar_processo` (`:883`, sets None).
     - `:606` (`_pos_revisao_concluida`) is reached only through the CONFIRMAR callback (`janelas.py:369-375`).
   - **`catalogo` writers:** `__init__` (`:174`) and `:607` only.
   - **Data flow:** `_ai_worker` hands `(DataFrame, catalogo)` to the UI thread (`:545, 550`), and `abrir_revisao_pdm` passes it to the review only.
   - Test at `:571`.

7. **#6b (second robot could start)** — ADDRESSED for the double start. See New Breakage for a side effect.
   - **Guard entry points:** `_robo_ocupado()` is the first line of `run_automation_thread` (`:619`) and `run_edicao_thread` (`:974`).
   - **Flag lifecycle:**
     - It is raised on the UI thread at the click (`:638`).
     - `_rodar_robo`'s `finally` clears it via `na_interface` (`:641-649`).
     - That clear is queued before `iniciar_tarefa`'s `_reabilitar`, so the button never returns while the flag is up.
   - **Early returns:** a missing backend and the validation refusals return before the flag is raised.
   - **Checks run:**
     - The robot constructor raising (outside the worker's try): `[ERRO]` is logged, the flag clears and the button returns.
     - Edição running: a creation click and a second edição are refused with the console message, and only one robot instance exists.
   - Test at `:1026` covers creation + creation and creation + edição.

### New Breakage in the Fix Diff

**Important: `cria_fichas.py:605-615` with `:648-649`. "4. Robô Web" stays disabled for good after a review is confirmed while the EDIÇÃO robot runs.**
- **Cause:**
  - `_pos_revisao_concluida` skips `btn_run_auto.setEnabled(True)` whenever `_robo_ativo` is up. Its comment says the button "volta sozinho no fim dele".
  - That holds only for the creation robot, because `iniciar_tarefa(botao=btn_run_auto)` gives that button back.
  - For the edição robot, `iniciar_tarefa` returns only `btn_run_edicao`, and `_robo_terminou` just clears the flag.
- **Reproduced** (scratch `test_rev_a_edicao_rodando_revisao_confirmada...`):
  1. Hold the edição robot in `iniciar_driver`.
  2. Run the Pular IA path, then confirm the review.
  3. Release the robot.
  - Result: `df_processed` is set, `_robo_ativo` is False and `btn_run_edicao` is enabled. `btn_run_auto` is still disabled 200 ms later.
  - The log says "Revisão OK. N itens prontos."
  - Recovery means redoing the whole AI step (toggle Pular IA or pick the PDM sheet, "3. Analisar", review, confirm) or Limpar.
- **Why Important:**
  - It is a regression against CTk, where confirm enables the button.
  - The sequence is reachable by normal use: the tab-2 robot runs for minutes while tab 1 is free.
  - It costs a paid AI re-run.
  - It is fail-safe: nothing wrong reaches the portal.
- **Test gap:** no test covers it. `test_um_robo_por_vez` has only the creation robot running at confirm.
- **Fix, verified on a scratch copy** (all 58 screen tests plus my 5 experiments pass, 63 in total): in `_robo_terminou`, after clearing the flag, add `if self.df_processed is not None: self.btn_run_auto.setEnabled(True)`. It is idempotent: after Limpar `df_processed` is None, and a creation robot already gets the button back. `test_rev_a_...` can serve as the regression test.

**Minor (test nit): `tests/test_qt_tela_cria_fichas.py:565-568`.**
- The two Pular IA toggles followed by `assert isEnabled()` cannot fail, because `_fim_da_cadeia_da_ia` already enabled the button. It is redundant, not wrong. The assertion at `:563` is what covers the flag.

**Two new deviations assessed:**
- **`self.catalogo` changes only at confirm.**
  - It is correct and safe: the batch and its catalogue now move as a pair, and the robot gets the pair at the click.
  - One edge: after an AI review closed with X, a following Pular IA review opens with the free-text editor, because the unconfirmed catalogue is no longer kept. CTk kept it. This is not a defect.
- **Robot mutual exclusion.**
  - The flag clears on every worker exit path I checked.
  - The only unguarded window is a synchronous failure inside `iniciar_tarefa` itself (thread start or destroyed button). That already leaves the button disabled on every screen.
  - The one gap is the stuck button above.

**Report claims:**
- The screen test count matches: 58 tests collected, 53 before plus 5 new. The first run of my scratch copy of the module also passed all 58 original tests.
- `ruff check` and pyflakes are clean on the two changed files (rerun in the archive).
- The RED breakdown "6 new + 8 contract" is off by one. The diff adds 5 new tests and changes 9 contracts. The total of 14 is right. This is a report-text issue only.
- I did not re-run `check.sh`, as instructed.

### Out-of-Scope Observations
- `resetar_processo` (`:876-926`, unchanged) clears `df_processed` but not `catalogo`. This matches CTk. Now that the two move together, a leftover remains: after Limpar, a Pular IA review opens with the old catalogue's chooser.

### Verdict
**Fix round:** All 7 findings are addressed, but the fix introduces one new Important breakage: "4. Robô Web" stays disabled after a review confirmed while the edição robot runs. It needs the 3-line fix above plus a test before this is clean. No new Critical issues.
