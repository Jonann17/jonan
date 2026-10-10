## Review E4.9 — Criação de Fichas (Qt), diff a37d43c..9838d2f

The review was read-only, and the checkout is clean at fc3ee97. Every test run used `git archive` snapshots in the scratchpad.

Line numbers below are from 9838d2f. `cria_fichas.py` and its tests are byte-identical at fc3ee97, and `blocos.py`/`espera.py` are unchanged there too.

Focused tests:
- **At 9838d2f:** cria_fichas 53, espera 14, copia_fichas 22, sem_tkinter 31 — all passed.
- **At fc3ee97:** the same suites pass, plus registro_telas 24.
- **Lint:** ruff and pyflakes are clean on the touched files.

### Spec Compliance

**(a) Same behaviour as the CTk screen**
- **Texts:** I compared every string literal in the two files (AST diff). Every user-visible string in the CTk screen is in the Qt one: titles, placeholder, log lines, messages and box titles. Only Tk layout tokens differ.
- **"Repetir/Cancelar":** these labels come from the `qtbase_pt_BR` translator that `main.py` installs (checked), so they match the "clique em 'Repetir'" text.
- **Robot branches:** SUCESSO / PULAR / RETRY / CHANGE_PDM / SKIP / STOP are kept in the same order.
- **"Preparo":** it appears after RETRY and after CHANGE_PDM, not after SKIP, and blocks the robot until OK. The SKIP portal reset is kept.
- **Button sequences:** initial state, `pos_selecao`, the toggle, the review callback, end of robot and Limpar all match CTk, apart from the documented deviations.

**(b) Thread safety**
- **Workers touch no widget.** Progress goes through `na_interface`, with a `RuntimeError` guard.
- **`JanelaAcaoRobo`** is called from the worker and returns `DecisaoRobo`. The window is built on the interface thread. X, hide or destroy all give STOP.
- **`JanelaResumo`** opens through `na_interface(self._fim_do_robo)`; a test checks it runs on the interface thread.
- **`avisar(esperar=True)` from a worker:** the box is posted to the interface thread and the worker waits on an Event. The Event is set in a `finally`, so a box that fails can't strand the worker.
- **`avisar(esperar=True)` from the interface thread:** it calls the box directly. This is the same branch `perguntar_sim_nao` uses, and `test_qt_perguntas` already tests it. No deadlock.
- **App exit:** goes through `instancia.encerrar`, so a worker parked on a wait does not keep the process alive.

**(c) The deviations and the ▶ glyph**
1. **X on the PDM review gives "3. Analisar" back — agree.** In CTk the flow was stuck; the only way out was toggling "Pular IA" or picking the PDM sheet again, and that re-ran the AI anyway. Like the other UX deviations, worth confirming with Luan.
2. **"Pular IA" / PDM sheet no longer re-enable "3. Analisar" during the AI step — agree.** This closes a real double run: two AI workers, both writing `df_processed`/`catalogo` and opening two reviews. The review itself is application-modal, so "during the review" can't happen anyway. One path is still open, though: picking the STATUS_PMIB rows again (Important #1).
3. **"Ver Resumo" brings the open window to the front — agree.** This matches the single-window rule from E4.3. There is a small leak, see Minor #3.
4. **▶ glyph — agree.** In the captures it is a plain triangle on both sides, slightly smaller in Qt. Qt 6 turns the QSS family list into `QFont.setFamilies`, so Windows will use Segoe UI Symbol. The button label is fixed text, so `estilo.mono` fits.

**(d) Lessons from earlier reviews**
- `mono` is used only on the two fixed labels (Limpar and Iniciar); log lines are untouched.
- Buttons use the `blocos` variants. `_pintar` rebuilds each stylesheet from `_folha_base`, so stylesheets don't pile up.
- All 9 buttons have no Enter default (there's a test for it).
- Esc on the review and robot dialogs is ignored (from E3.2). The Preparo and Arquivo Aberto boxes behave like the Tk messageboxes.
- Each chain has a single task, so buttons are not re-enabled mid-chain (but see Minor #2).
- Widget fields are read at click; screen state is not (Important #1).

**(e) `BarraDeProgresso` move**
- Moved verbatim to the end of `blocos.py`.
- `copia_fichas.py` uses it, and the unused `QProgressBar` import was removed.
- No references to `_BarraDeProgresso` remain.
- The Cópia tests pass 22/22 at both commits.

### Strengths
- A careful port of the largest screen.
- Shared changes are minimal and kept in separate blocks: one keyword-only parameter on `avisar`, and a verbatim class move.
- Strong tests: 53 tests covering the whole decision loop, the Preparo wait, the summary merge, salvar retry/cancel, the edição tab, non-daemon threads, and geometry for both tabs at 6 window heights.
- The `_ia_em_andamento` chain is a clean answer to the double-run bug.
- The ▶ symbol-font fallback is well reasoned.
- I checked the parity claims in the captures and they hold, apart from Minor #4.

### Issues

**Critical:** none.

**Important**

1. **`cria_fichas.py:457, 479, 485, 489` — the AI worker reads screen state, not a copy taken at the click.**
   - **What:** `_ai_worker` still reads `self.df_data_selecionado` and `self.file_path_pdm` live. "Selecionar Excel (.xlsx)" stays enabled during the AI step, which can take minutes.
   - **Effect:** if the person picks other rows mid-run, the descriptions are swapped under the AI answers.
   - **Reproduced on a scratch copy:** the AI answered for rows A and B, and the review received `[('A','C'), ('B','D')]` — the PDMs chosen for A/B, silently labelled with C/D's descriptions. A wrong PDM reaches the portal unless the reviewer happens to notice.
   - **Why it matters here:** this is inherited from CTk. But it is the cross-thread race the brief says to fix ("bugs de thread corrigidos", read on click), and the port already takes `cod_proj`/`pular` at the click and blocks the other mid-chain changes.
   - **Fix:** in `run_ai_thread` (428–449), take `df = self.df_data_selecionado` and `caminho_pdm = self.file_path_pdm` (plus the key) and pass them as arguments; the worker uses only those.
   - **Test to add:** choose new rows while `processar_lote` is blocked; the review keeps the original descriptions.

**Minor**

2. **`cria_fichas.py:525–530, 547–554`, with `resetar_processo` at 796–846 and the flag at 168 — a failure while opening the review locks "3. Analisar" for good.**
   - **What:** if anything raises while the review opens (`JanelaRevisaoPDM(...)` inside `_depois_da_ia`), the interface bridge swallows the exception and `_ia_em_andamento` stays True.
   - **Effect:** the button stays dead for the screen's lifetime. Limpar doesn't reset the flag, and the flag now blocks the toggle and PDM pick that recovered it in CTk.
   - **Reproduced:** `(flag, enabled)` was `(True, False)` after the failure and still `(True, False)` after Limpar plus two toggles. The manual flag loses `iniciar_tarefa`'s "always give the button back" guarantee.
   - **Fix:** wrap the interface-side continuation in try/except, then log and call `_fim_da_cadeia_da_ia()`. Minor because nothing is known to trigger it.

3. **`cria_fichas.py:744–759` (758) — closed summary windows pile up.**
   - **What:** each "Ver Resumo" after a close builds a new `JanelaResumo`, and the closed one stays as a hidden child of the screen, holding the whole table.
   - **Reproduced:** 3 open/close cycles left 3 `JanelaResumo` children. CTk's `destroy()` freed them.
   - **Fix:** set `WA_DeleteOnClose` on the window created here (the existing `RuntimeError` guard in `_mostrar_resumo` already covers a deleted window), or `deleteLater()` the replaced one.

4. **`cria_fichas.py:61–69`, used at 205, 215, 306, 315 — four labels have the wrong gray.**
   - **What:** "Código do Projeto:", "Arquivo STATUS_PMIB:", "Novo Código do Projeto:" and "Selecionar Fichas (Excel):" have no `cor`, so they take the app's `text_light` #E0E0E0. A CTkLabel with no `text_color` is gray84, #D6D6D6.
   - **Measured in the task's own captures:** CTk 214, Qt 224. The report's "cores idênticas" table didn't sample these labels.
   - **Fix:** busca_pmib, pdm, lmr and pmib_manager use `controles.COR_TEXTO_CTK` for this case. Default `_rotulo` to it.

5. **`cria_fichas.py:939` — the edição "Concluído" box no longer waits.**
   - **What:** in CTk the `showinfo` blocked the worker before its `finally`. Now the browser closes and "Iniciar Robô de Edição" comes back before the person clicks OK.
   - **Why it's minor:** harmless, and consistent with how other screens show their final notice, but it isn't listed among the deliberate deviations.
   - **Fix:** list it in the report, or use `esperar=True` for strict parity.

6. **Inherited from CTk, not port defects — candidates for `PENDENCIAS.md`:**
   - **(a) Robot can run unreviewed data.** `_ai_worker` writes `self.df_processed` (518) before the review is confirmed. If a previous batch left "4. Robô Web" enabled, closing the new review with X leaves the robot pointed at unreviewed data.
   - **(b) A second robot can start.** `_pos_revisao_concluida` (563–569) re-enables "4. Robô Web" even while a robot is running; after a chain, "Pular IA" re-enables "3. Analisar" as in CTk. A second robot could then start, and the first robot's final merge (670) would use the new `df_processed`.

### Assessment
**Needs fixes** — small ones:
- Important #1 is about 5 lines plus one test.
- Minors #2–#4 are cheap; I recommend doing them in the same fix commit.
- #5 only needs a line in the report.
- #6 goes to `PENDENCIAS.md`.

Everything else checks out: the same behaviour as CTk, thread safety, the three deviations, the ▶ glyph, the earlier review lessons, and the progress-bar move.

Experiments: scratchpad `rev49/snap2/tests/test_rev_e49.py`, the `rev_` tests. Report reviewed: `/home/user/sig-ft/.superpowers/sdd/etapas3a6/e4.9-report.md`.
