# E6.2 — Empacotamento: o `.exe` leva a interface Qt

Onde a tarefa se encaixa: a E6.1 fez `frontend.py` abrir a interface Qt por padrão (`--ctk`
abre a antiga), o `--smoke` da Qt grava `conferencia-da-janela.txt` e visita todas as telas, e
`sigft/app/conferencia.py` confere os módulos Qt. Falta o pacote: hoje o `SIG-FT.spec` deixa a
Qt DE FORA de propósito (filtro em `collect_submodules("sigft")` e `"PySide6"`/`"shiboken6"`
nos `excludes`, com o comentário "A Etapa 6 remove este filtro"). Sem esta tarefa, o `.exe`
abriria a Qt sem a Qt dentro.

Worktree isolada de /home/user/sig-ft; confira que `git log` contém o commit da E6.1 (o
controlador diz qual no despacho). Commit na sua worktree; o controlador faz cherry-pick.
**Nunca dê push.** Leia /home/user/sig-ft/.superpowers/sdd/qt-convencoes.md e o `CLAUDE.md`.

## Requisitos

### A. `SIG-FT.spec`
- Tire o filtro de `sigft.app_qt` e os `excludes` de PySide6/shiboken6; reescreva os
  comentários que explicavam a exclusão.
- Tudo o que a Qt lê do disco tem de ir junto e ser encontrado DENTRO do pacote: as fontes de
  `sigft/app_qt/estilo.py` (`PASTA_FONTES`, `ARQUIVOS_DE_FONTE`), imagens e ícones usados por
  `sigft/app_qt/`, e traduções do Qt se o código carregar alguma (`grep -rn "QTranslator\|qm"
  sigft/app_qt`). Confira como cada caminho é resolvido no pacote (`sys._MEIPASS` vs
  `__file__`); se algum não resolver, corrija no código com teste.
- Só o que o app usa: plugins e módulos Qt que ninguém importa ficam fora (meça o efeito).
- Licença: o PySide6/Qt é LGPLv3. Inclua no pacote os textos de licença que o wheel traz e
  diga no relatório onde ficaram.

### B. `release.yml` e documentação de build
- Ajuste o que precisar para o Release montar o `.exe` com a Qt (o workflow instala
  `requirements.txt` + `requirements-dev.txt`; confira se nada mais exclui ou pressupõe
  CustomTkinter-only, inclusive o instalador e a atualização pequena descrita em
  `docs/BUILD.md`).
- `docs/BUILD.md`: atualize as partes que falam da Qt fora do pacote.

### C. Validação local (Linux, como substituto do Windows)
- Num venv de rascunho (não mexa em `/home/user/sig-ft/.venv`), com `requirements.txt` e
  `pyinstaller>=6,<7`, rode `pyinstaller SIG-FT.spec --noconfirm --clean`.
- Rode o pacote: `--conferir-pacote` (relatório limpo), `--smoke` com
  `QT_QPA_PLATFORM=offscreen` (relatório limpo, todas as telas), e abra-o no Xvfb (captura).
- Meça: tamanho de `dist/SIG-FT` antes (spec antigo) e depois, e o tempo até a janela
  aparecer; ponha os números no relatório.
- Diga no relatório o que NÃO dá para validar aqui (o `.exe` no Windows, o instalador, a
  assinatura) e o que o Luan precisa olhar no primeiro Release.
- Apague `build/`, `dist/` e o venv de rascunho no fim (disco limitado).

## Verificação (antes do commit)
- `bash scripts/check.sh` "TUDO OK" e `/home/user/sig-ft/.venv/bin/ruff check .` limpo.
- Um commit local: "Qt6: pacote do Release leva a interface Qt" (sem acento, rodapé das
  convenções).

## Relatório
Completo em /home/user/sig-ft/.superpowers/sdd/etapas3a6/e6.2-report.md. Responda só com o
contrato curto: Status, commit SHA + assunto, uma linha de testes, preocupações, caminho do
relatório.
