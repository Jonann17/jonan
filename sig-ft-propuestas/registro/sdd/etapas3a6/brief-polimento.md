# Polimento — o que as revisões deixaram para o fim

Onde a tarefa se encaixa: todas as telas Qt estão portadas, revisadas e integradas, e o corte
(E6.1) fez a Qt ser a interface oficial. As revisões de cada tarefa deixaram detalhes que
valiam para várias telas de uma vez; foram guardados para uma tarefa só, no fim, para não
pisar no trabalho em paralelo. É esta.

Worktree isolada de /home/user/sig-ft; o controlador diz no despacho qual commit ela tem de
conter. Commit na sua worktree; o controlador faz cherry-pick. **Nunca dê push.** Leia
/home/user/sig-ft/.superpowers/sdd/qt-convencoes.md (paridade visual medida no Xvfb, TDD,
verificação) e o `CLAUDE.md` (arquivos do Rafael não se editam).

Regra geral: **comportamento não muda** (a não ser o item B4, que é decisão já tomada) e o
visual só se aproxima do CustomTkinter. Item que exigiria mudar comportamento ou uma
reforma grande: não faça, explique no relatório.

## A. Visual (medir CTk × Qt no Xvfb antes e depois; capturas no relatório)
1. **Console:** o texto do console está 4 px à esquerda e 5 px acima do CTk em todas as telas
   (`ConsoleFrame` / `#console`). Corrija no compartilhado.
2. **Negrito longo:** sai ~9% mais largo que o Tk (título do PDM 291 px × 266; INICIAR do
   Upload 212 × 202). Remeça a decisão do commit 66b4cc5 (negrito sintético do Roboto Regular
   + hinting) em títulos longos; se houver um ajuste barato que aproxime sem piorar os textos
   curtos, aplique; se não, deixe medido no relatório. Limite: não troque a fonte do app.
3. **Nome de arquivo longo** (> ~85 caracteres) alarga o formulário além da janela (pdm,
   pmib_manager, `_upload_comum`, pickers): elida com `QFontMetrics.elidedText` num lugar só
   (caminho completo no tooltip). Os testes de geometria do PDM ganham tolerância em y/h só
   onde a medida depende de fonte.
4. **Área com barra sempre visível:** há cópias locais (Analyzer, AutoSpec
   `_area_como_a_do_ctk`, e o bloco de folha repetido em autospec/copia_fichas/cria_fichas).
   Um parâmetro em `blocos.area_rolavel` (barra sempre visível e o recorte de 6 px do CTk) e
   as telas passam a usá-lo.
5. **Rádio e aba:** a largura mínima 100 do CTkRadioButton e a altura da aba seguindo a aba
   selecionada foram feitas localmente no `pdm.py`; leve para `estilo`/`Abas`.

## B. Código repetido e acúmulo
1. `_marcar_escolhido` acumula stylesheet a cada escolha (pdm, pmib_manager,
   `_upload_comum`): reconstrua a folha a partir da base, como `cria_fichas._pintar`.
2. `VAO_TEXTO_CAIXA` duplicado: `dialogs.py` usa o de `controles`.
3. `_perguntar` (correcao_pdm) duplica `DialogosDeEspera.perguntar_sim_nao`: acrescente ao
   compartilhado o parâmetro do botão padrão e use-o; corrija o comentário "1 px por letra".
4. **Foco dos botões:** os botões de tela pegam foco e o Espaço os aperta; o CTkButton nunca
   pegava foco. Decisão: `blocos.botao` cria botões sem foco (como `dialogs.sem_tecla`), em
   todas as telas. Confira que nenhum fluxo de teclado existente depende disso. O
   `NovasListasDialog` do pmib_manager (segura o worker) passa a usar `dialogs.sem_tecla`.
5. Rótulos: `_rotulo` quase duplicado em `views/home.py` e `widgets/mural.py` → um helper
   (em `blocos`, se couber); o `font-family` de símbolos repetido em autospec e cria_fichas →
   um helper no `estilo`, e some o alias de `FAMILIAS_COM_SIMBOLO` do cria_fichas.
6. `_texto_dos_avisos` do pmib_manager é cópia do CTk: leve para um módulo sem tkinter que os
   dois lados usam (padrão de `sigft/app/textos_dialogos.py`); a CTk delega.
7. Atualização (E5.2): o aviso fechado só é escondido → `deleteLater`; o QSS local da caixa de
   notas e da barra vai para o `estilo`.
8. `dialogs.py`: três linhas em branco entre `sem_tecla` e `SoltaAoFechar`.

## Verificação (antes do commit)
- TDD onde houver comportamento (B1, B3, B4, A3, A4); os testes de geometria existentes
  continuam passando (ajuste só o que a correção visual mudou, explicando).
- `bash scripts/check.sh` "TUDO OK" e `/home/user/sig-ft/.venv/bin/ruff check .` limpo.
- `python frontend.py --smoke` (com `QT_QPA_PLATFORM=offscreen`) limpo.
- Um commit por grupo (A e B), sem acento, rodapé das convenções.

## Relatório
Completo em /home/user/sig-ft/.superpowers/sdd/etapas3a6/polimento-report.md (se a worktree
não puder gravar lá: /tmp/claude-0/-home-user/111ccf73-6723-5e3b-a4c3-03916583ae47/scratchpad/capturas/polimento/polimento-report.md),
com a tabela de medidas antes/depois. Responda só com o contrato curto: Status, commits SHA +
assunto, uma linha de testes, preocupações, caminho do relatório.

## C. Achados das últimas revisões (pequenos)
1. `tests/test_mural_atividades.py::test_as_homes_nao_leem_a_planilha` é contornável
   (`from openpyxl import load_workbook` chamado como nome solto passa): conferir
   `no.module.split(".")[0]` e chamadas `ast.Name`, como `tests/test_atividades.py:226-238`.
2. `test_le_as_colunas_e_classifica` preenche só 5 das 10 colunas mapeadas: preencher todas,
   para que trocar uma coluna por outra deixe o teste vermelho.
3. `sigft.services.mural_atividades` entra na lista de `tests/test_qt_sem_tkinter.py`.
4. Docstring de `sigft/app_qt/views/home.py` (linhas 5-9) cita os serviços usados: falta
   `services.mural_atividades`.
5. `sigft/services/mural_atividades.py:43`: `os.listdir` fora de qualquer `try` — uma
   `PermissionError` na pasta lembrada escapa do botão em vez de virar o texto de erro
   amigável (herdado da CTk, que agora delega ao mesmo serviço). Trate dentro do serviço,
   com teste; vale para as duas interfaces, diga no relatório.
