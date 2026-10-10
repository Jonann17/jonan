# E6.1 — Corte: o app abre a interface Qt pelo caminho normal

Onde a tarefa se encaixa: migração CustomTkinter → Qt (PySide6). As telas Qt estão prontas e
registradas em `sigft/app_qt/main.py` (`TELAS`, fábricas com import na primeira visita). Hoje a
interface Qt só abre com `python -m sigft.app_qt.main`; `python frontend.py`, o `SIG-FT.bat` e o
`.exe` abrem a CTk. Esta tarefa faz a Qt ser a interface oficial, mantendo a CTk acessível com
`--ctk` durante a transição. O empacotamento (`SIG-FT.spec`, `release.yml`) é a tarefa seguinte
(E6.2) — **não mexa neles aqui**.

Worktree isolada de /home/user/sig-ft. Confira `git log --oneline -3`: tem de conter fc3ee97
("uploads com erro de JSON..."); se não, `git merge --ff-only local/jonan-cambios` ou reporte.
Commit na sua worktree; o controlador faz cherry-pick. **Nunca dê push.**

Leia antes: /home/user/sig-ft/.superpowers/sdd/qt-convencoes.md (convenções, venv, captura no
Xvfb, verificação) e o `CLAUDE.md` do repo (frontend.py: as três verificações, inclusive ABRIR
o app; arquivos do Rafael não se editam; nada de reformatar arquivo compartilhado).

## Requisitos

### A. `frontend.py` abre a Qt por padrão
- Logo depois do `_despachar_cedo()` e ANTES dos imports do CTk: se `__name__ == "__main__"` e
  `"--ctk"` não está em `sys.argv`, chame `sigft.app_qt.main.executar_da_linha_de_comando()`
  e não continue (confira se ela pode voltar; se puder, saia logo depois). Assim o modo Qt nunca
  importa tkinter/CustomTkinter.
- Com `--ctk`, tudo como hoje (inclusive `--ctk --smoke`).
- Os reexports do topo continuam: quem faz `import frontend` segue recebendo os nomes do CTk.
- Atualize o parágrafo da docstring sobre "a forma de abrir o aplicativo".
- Diff mínimo: arquivo compartilhado.

### B. `--smoke` da Qt faz o mesmo papel do `--smoke` do CTk no Release
O `release.yml` roda `SIG-FT.exe --smoke` e lê `conferencia-da-janela.txt` (o `.exe` é
`console=False`: o que ele imprime não chega ao CI). Hoje o `_smoke` da Qt só imprime.
- Grave o relatório com `sigft.app.conferencia.gravar_relatorio(ARQUIVO_JANELA, ...)` nos dois
  caminhos (sucesso e falha), avisos de backend incluídos — veja `_smoke` em
  `sigft/app/main.py` e o porquê nos comentários de lá.
- As telas Qt são criadas na primeira visita, então um módulo de tela faltando no pacote só
  apareceria no uso. O smoke visita TODAS as telas de `TELAS` (menos as de
  `catalogo.TELAS_BLOQUEADAS`); tela que vira `TelaComErro` = falha, com o nome da tela e o
  motivo no relatório.

### C. `sigft/app/conferencia.py` (continua só stdlib) confere a Qt
- `MODULOS_ESSENCIAIS` ganha `PySide6.QtCore`, `PySide6.QtGui`, `PySide6.QtWidgets`,
  `shiboken6`, `sigft.app_qt.main` e cada módulo de tela importado pelas fábricas de `TELAS`.
- Um teste trava as duas listas juntas (tela nova registrada em `TELAS` sem entrar na
  conferência = teste vermelho).
- `customtkinter` fica enquanto existir `--ctk`.

### D. Dependências
- `PySide6-Essentials>=6.9` passa para o `requirements.txt`, com comentário do porquê (é a
  interface oficial; o `SIG-FT.bat` reinstala sozinho na próxima abertura porque o hash do
  arquivo muda; ordem de grandeza do download).
- O CI instala só o `requirements-dev.txt`: siga o padrão do `lxml` lá (dependência de
  produção repetida, com o comentário do porquê). Remova o `requirements-qt.txt` e atualize
  toda referência a ele (`grep -rn requirements-qt`).

### E. Lançador para macOS
- `SIG-FT.command` (clique duplo no Finder) + `scripts/_bootstrap_venv.sh`, com o mesmo
  comportamento de `SIG-FT.bat` + `scripts/_bootstrap_venv.bat` naquilo que vale no Mac:
  - exige `python3` >= 3.10 (mensagem clara com o link do python.org se não houver);
  - venv em `<raiz>/.venv`; se a pasta estiver num serviço de sincronização (iCloud Drive,
    OneDrive, Dropbox, Google Drive), em `~/Library/Application Support/SIG-FT/venv`;
  - instala o `requirements.txt` só quando o arquivo mudou (carimbo com o hash, como o `.bat`);
  - navegador do Playwright uma vez, sem derrubar a instalação se falhar (como o `.bat`);
  - roda `frontend.py` a partir da raiz;
  - em caso de erro, a janela do Terminal fica aberta com a mensagem.
- Bit de execução gravado no git (`git update-index --chmod=+x`).
- Teste: `bash -n` nos dois scripts e o bit de execução conferido; a lógica do carimbo testada
  de verdade se der para isolar numa função.

### F. Documentação mínima
README: como abrir (Windows `SIG-FT.bat`, Mac `SIG-FT.command`, a primeira abertura no Mac
pelo botão direito → Abrir, `--ctk` para a interface antiga). Nada além disso.

## Verificação (antes do commit)
- TDD onde houver código (`frontend.py`, `_smoke`, conferência, scripts).
- `bash scripts/check.sh` termina "TUDO OK" e `/home/user/sig-ft/.venv/bin/ruff check .` limpo.
- **Abrir o app de verdade** no Xvfb com o venv312 das convenções: `python frontend.py`
  (tem de ser a Qt) e `python frontend.py --ctk` (tem de ser a CTk) — capture as duas; e
  `python frontend.py --smoke` com `QT_QPA_PLATFORM=offscreen` gravando o relatório.
- Um commit local: "Qt6: frontend.py abre a interface Qt (--ctk abre a antiga) e lancador
  para macOS" (sem acento, rodapé das convenções).

## Relatório
Completo em /home/user/sig-ft/.superpowers/sdd/etapas3a6/e6.1-report.md (o que fez, TDD
RED/GREEN, testes, ruff, as aberturas reais com as capturas, desvios com o porquê, arquivos,
preocupações). Responda só com o contrato curto: Status, commit SHA + assunto, uma linha de
testes, preocupações, caminho do relatório.
