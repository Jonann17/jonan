### Spec Compliance
- ✅ **Spec compliant.** I checked every requirement in the brief against the diff and the 7febd4e tree.
  - **A. Qt opens by default:**
    - The Qt dispatch sits right after `_despachar_cedo()` and before the CTk imports (`frontend.py:62-69`; the CTk imports start at `:71`).
    - `sys.exit(0)` catches a Qt that returns, and a test covers it.
    - `--ctk` and `--ctk --smoke` fall through unchanged, and `import frontend` still gets the re-exports.
    - The docstring paragraph is rewritten and the diff stays minimal.
  - **B. Smoke report and screen visits:**
    - `_smoke` writes `ARQUIVO_JANELA` through `conferencia.gravar_relatorio` on both paths, with the backend warnings (`sigft/app_qt/main.py:458,475,492`).
    - `_visitar_telas` (`:428`) visits every key in `TELAS` except `TELAS_BLOQUEADAS`, through `show_frame`.
    - `show_frame` turns *any* `Exception` into `TelaComErro` (`:234-241`). So every broken screen is reported with its name, reason and traceback, and the exit code is 1.
  - **C. Conferência covers Qt:**
    - PySide6.QtCore/QtGui/QtWidgets, `shiboken6`, `sigft.app_qt.main` and all 13 screen modules are in the list, including the blocked `correcao_pdm` (`sigft/app/conferencia.py:57-91`).
    - The file is still stdlib-only, and `customtkinter` stays, with a comment.
    - The test that locks the two lists checks both directions (`tests/test_conferencia_do_pacote.py:321-369`).
  - **D. Dependencies:**
    - `PySide6-Essentials>=6.9` is in `requirements.txt`, with the why, the automatic reinstall, and the download size. "Maior download da lista" is true: there is no torch or similar in the list.
    - It is repeated in `requirements-dev.txt`, following the lxml pattern.
    - **Named risk (b):** `grep -rn requirements-qt` over a `git archive 7febd4e` copy finds no reference left anywhere.
  - **E. Mac launcher:**
    - `SIG-FT.command` + `scripts/_bootstrap_venv.sh` mirror `SIG-FT.bat` + `_bootstrap_venv.bat` point by point:
      - same venv order;
      - stamp written only after a pip run that succeeded;
      - same pip-arguments precedence;
      - Playwright browser once, never fatal.
    - It requires Python 3.10+ and gives the python.org link, runs `frontend.py` from the root, and waits for Enter on error (`SIG-FT.command:21-29,48`).
    - Both files are `100755` in `git ls-tree`. The `bash -n` test, the exec-bit test and the real stamp tests are present.
  - **F. README:** covers Windows, the Mac double-click, the first open by right-click → Open, and `--ctk`.
  - **Verification:**
    - The commit subject and footer are correct.
    - The captures exist: `python frontend.py` shows the Qt Home, and `--ctk` shows the CTk Home (its scrollbars are always visible).
    - The Qt smoke report lists 12 screens OK and CorrecaoPDM as blocked.
  - **Extras:** all small and justified:
    - the `TelaNaoMigrada` text now points to `--ctk`;
    - `.command` forwards `"$@"`;
    - the README has a macOS 15 "Abrir Mesmo Assim" line and a line on where the venv goes;
    - the pip error mentions macOS 12.
- ⚠️ **Cannot verify from diff:**
  - **Mac-only behaviour:** a real bash 3.2 run, Gatekeeper on a `.command` downloaded in a ZIP, how the Terminal window behaves, skipping `/usr/bin/python3` when the Command Line Tools are missing, and the iCloud "Mesa e Documentos" symlink heuristic. The suite only runs these scripts under the CI's bash 5.
  - **Named risk (c), bash 3.2:**
    - By inspection, plus a grep for bash-4-only syntax (`;;&`, `${x,,}`, `mapfile`, `declare -A`, `[[`, `|&`, `printf -v`…): only comments match.
    - Everything used (functions, `local`, `${BASH_SOURCE[0]}`, `${v%pat}`, `set --`, `command -v`, `read -r -p`) exists in bash 3.x.
    - The one construct that depends on a shell option is `"${linha%$'\r'}"` (`scripts/_bootstrap_venv.sh:190`), which bash 3.x expands through `extquote` (on by default).
    - I ran the real function on bash 5.2 with a CRLF `pip_corporativo.txt`, and it strips the CR. I could not get a bash 3.2 binary (the proxy blocks ftp.gnu.org), so 3.2 itself is unproven.
  - The test that reads factory bytecode, under CI's Python 3.10 (the implementer checked only 3.12 and 3.13).
  - `SIG-FT.bat` → Qt on a real Windows machine (only Linux/Xvfb was verified).

### Strengths
- The `frontend.py` edit is small and in exactly the right place. The safety-net `sys.exit(0)` is tested with a fake Qt that *returns*.
- The cut is proved by behaviour, not by mocks:
  - a clean interpreter with a `MetaPathFinder` that makes any tkinter/customtkinter import fail;
  - a real Qt `--smoke` through the entry point with Tk blocked, so only Qt can write the report;
  - `/proc/<pid>/maps` checks in the real openings.
- The smoke reuses the `show_frame` path instead of duplicating factory logic, collects *all* broken screens, and `TelaComErro.erro` is the smallest possible hook.
- The test locking the conferência to `TELAS` reads the live factories, checks both directions, gives actionable messages, and actually caught the AutoSpec registration during the rebase.
- Because the bootstrap only defines functions when sourced, the tests can run the real scripts with a fake `python` that records its calls. They cover:
  - the stamp, and a pip failure that leaves no stamp;
  - the sync-folder table, including a negative case;
  - a first run end to end;
  - the error path waiting for Enter.
- Test isolation is right: the in-process smokes `chdir(tmp_path)`, and the subprocess smoke sets `SIGFT_DADOS_DIR`, which `caminho_config()` honours.

### Issues
#### Critical (Must Fix)
None.

#### Important (Should Fix)
None.

#### Minor (Nice to Have)
1. **Named risk (a): when PySide6 is missing or broken, nothing leads to `--ctk`** (`frontend.py:63-65`, `SIG-FT.bat:27`, `README.md:103`). What the person sees:
   - **pip cannot download PySide6.** Every existing venv reinstalls on its next opening because the hash changed: about 80 MB, possibly through a corporate proxy. `_bootstrap_venv.bat:171-177` → `SIG-FT.bat:18` → "Encerrado com erro" + `pause`. Neither interface opens, even though the CTk one does not need PySide6. The next opening tries again. This follows from requirement D plus the launcher's existing abort-on-pip-failure policy, so it is accepted. It deserves a line in the E6.3 notice.
   - **PySide6 is installed but fails to load** (e.g. `DLL load failed while importing QtCore`). The person sees a raw traceback, then `SIG-FT.bat:28` → `pause`.
     - Nothing mentions `--ctk`.
     - `SIG-FT.bat` does not forward `%*`.
     - The README's `python frontend.py --ctk` uses a bare `python`, which for a `.bat` user is the system interpreter without the venv's packages.
     - So the fallback exists but is hard to find exactly when it is needed.
   - **Mac:** the same two cases, but the message stays on screen until Enter ✓. `./SIG-FT.command --ctk` works, but needs a Python with Tk.
   - **Fix:** wrap the import at `frontend.py:63` in `try/except ImportError`, print a short message giving the full command `"{sys.executable}" "<frontend.py>" --ctk`, then `sys.exit(1)`. Optionally add `%*` at `SIG-FT.bat:27`.
2. **If the Qt import fails at load time under `--smoke`, no report is written and the Release step hangs.**
   - `frontend.py:63` imports `sigft.app_qt.main`, which loads the PySide6 binaries, dotenv and four views at module level (`sigft/app_qt/main.py:23-39`). That happens before `_smoke()`'s `try` (`:450`).
   - In the windowed `.exe` (`SIG-FT.spec:338-339`: `console=False`, `disable_windowed_traceback=False`), PyInstaller shows the traceback in a dialog. `Start-Process -Wait` then blocks until `timeout-minutes: 5` (`release.yml:198`), and the "(o .exe nao gravou…)" line (`:209`) never prints.
   - `--conferir-pacote` does not catch this: it uses `find_spec` (`conferencia.py:169`), which never loads `QtCore.pyd`. That is exactly why `conferir_tradutor` got a real-load check.
   - The CTk path has the same gap, so B is met as written. But the cut moves the smoke onto the binary-heavy toolkit just before E6.2 bundles it for the first time.
   - **Fix:** in the same `try` as item 1, when `--smoke` is in `argv`, call `gravar_relatorio(ARQUIVO_JANELA, traceback.format_exc())` and exit 1. And/or have E6.2 add a real `import PySide6.QtWidgets` check next to `conferir_tradutor`.
3. **iCloud "Mesa e Documentos" detection relies on an unverified signal, and its comment understates the risk** (`scripts/_bootstrap_venv.sh:97-110`; the comment is at `:100-101`).
   - The comment says the worst case is the venv in Application Support. That is only true for a false positive.
   - A false negative puts `<raiz>/.venv` (tens of thousands of files) in an iCloud-synced folder — exactly the case E exists to prevent. With "Otimizar Armazenamento", iCloud can also evict venv files, which causes intermittent ImportErrors.
   - Unzipping to Desktop/Documents is common, and macOS setup offers to sync those folders to iCloud.
   - **Fix:** a false positive costs nothing, so treat any project under `$HOME/Desktop` or `$HOME/Documents` as synced unconditionally, and fix the comment (`README.md:65-67` would follow).
4. **No `eol=lf` rule for the new shell scripts.** `.gitattributes:8` pins line endings only for `*.bat`.
   - A Windows checkout with Git for Windows' default `core.autocrlf=true` turns `SIG-FT.command` and `_bootstrap_venv.sh` into CRLF files.
   - A folder copied or zipped from such a checkout fails on line 1 with `/bin/bash^M: bad interpreter`.
   - GitHub's Download ZIP is safe today: the files are stored as LF with no CR bytes (verified).
   - **Fix:** add `*.sh text eol=lf` and `*.command text eol=lf`, following the `.bat` precedent.
5. **Test nits:**
   - `tests/test_lancador_mac.py:91`: without git, the test errors with `FileNotFoundError` instead of skipping. Catch it and skip.
   - `tests/test_qt_corte.py:96`: it only asserts `"[smoke]"`, which the CTk report also contains. Asserting `"telas visitadas"` would make the intent explicit.
   - `tests/test_conferencia_do_pacote.py:333-337`: a `functools.partial` or a class registered in `TELAS` would raise `AttributeError` instead of the actionable message.
6. **Sequencing (no code change):** I confirmed that `SIG-FT.spec:175-180,242-246` still excludes PySide6/shiboken6 and filters out `sigft.app_qt`. A Release before E6.2 stops safely at `--conferir-pacote`. A local `Gerar-Executavel.bat` build in between would produce an `.exe` that opens Qt without Qt inside, so land E6.2 before any build.
7. **Noise in the reported output:** the suite's 19 warnings come from `test_autorizados`, `test_painel` and `test_pmib_manager_v2`, which predate this task; none comes from its 69 tests. The `invalid command name …update` lines in the CTk capture log are normal CTk shutdown noise. Neither is E6.1's to fix.

### Assessment
**Task quality:** Approved
**Reasoning:** All of A–F is implemented as briefed. The tests check real behaviour (Tk blocked, a real Qt smoke through the entry point, the real launcher scripts), and the real openings match what the report claims. The findings are hardening of failure paths and Mac-only behaviour that can't be checked here. Items 1 and 2 share one small `try` in `frontend.py` and are worth folding into E6.2.
