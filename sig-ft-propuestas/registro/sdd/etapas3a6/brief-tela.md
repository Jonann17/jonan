# Brief comum das tarefas de tela (E3.2 e E4.x)

Você está numa worktree isolada de /home/user/sig-ft (confira `git log --oneline -3`: deve conter 2f3dbea "arquivos travados minimizavel..." (telas lancadas antes podem estar em 684f976; tudo bem); se não, `git merge --ff-only local/jonan-cambios` ou reporte). Commit na sua worktree; o controlador faz cherry-pick. Nunca dê push.

1. Convenções obrigatórias: /home/user/sig-ft/.superpowers/sdd/qt-convencoes.md
2. Plano: /home/user/sig-ft/.superpowers/sdd/etapas3a6/plano.md (você faz SÓ a sua tarefa).
3. API dos widgets compartilhados prontos (USE-os, não duplique): /home/user/sig-ft/.superpowers/sdd/etapas3a6/e3.1-report.md (dialogos_selecao: SelecaoMultiplaDialog, TabelaSelecaoDialog, ArquivosTravadosDialog; pickers.FileQueueList; painel_janela.JanelaPainel; abas.Abas = CTkTabview; estilos de radio/slider/treeview/progresso; blocos.barra_progresso, blocos.modo_indeterminado, blocos.botao(cor_fundo=, cor_hover=), blocos.area_rolavel, blocos.geometria_tk) e widgets/controles.py (Interruptor = CTkSwitch, MenuDeOpcoes = CTkOptionMenu, caixa de marcar). Telas de referência: sigft/app_qt/views/translator.py, apagar_lmr.py, lmr.py (+ testes tests/test_qt_tela_*.py).
4. NÃO edite sigft/app_qt/main.py nem catalogo.py (o registro em TELAS é feito na integração). Para capturar, registre a tela só dentro do seu script de captura.
5. Se precisar mudar código compartilhado (estilo.py, blocos.py, widgets/*), faça o mínimo, em bloco separado, e liste no relatório (outras telas rodam em paralelo).
6. Paridade visual com captura real CTk × Qt (a tela inteira e cada diálogo/pop-up que ela abre), medida com PIL. Capturas em $CAP/<tarefa>/.
7. Comportamento idêntico à tela CTk (textos, mensagens, ordem, regras), bugs de thread corrigidos; todo desvio com o porquê no relatório.
8. Antes do commit: `bash scripts/check.sh` (TUDO OK) e `/home/user/sig-ft/.venv/bin/ruff check .`.
9. O relatório: a worktree pode não conseguir escrever em /home/user/sig-ft/.superpowers; escreva em $CAP/<tarefa>/<tarefa>-report.md (CAP=/tmp/claude-0/-home-user/111ccf73-6723-5e3b-a4c3-03916583ae47/scratchpad/capturas) e diga o caminho.
