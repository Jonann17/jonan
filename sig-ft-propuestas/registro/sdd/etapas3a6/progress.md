# Ledger etapas 3-6 — plano: /home/user/sig-ft/.superpowers/sdd/etapas3a6/plano.md
E5.2: complete (1f1c72c no ramo worktree-agent-a66ee63128ce6a574, review approved; falta cherry-pick)
E5.2: minor (deferred): aviso fechado so escondido (sem deleteLater); QSS da caixa de notas e da barra local -> mover p/ estilo apos E3.1; "Atualizar agora" nao olha tarefas_em_andamento (igual CTk, PENDENCIAS)
E3.1: complete (684f976 + fix 2f3dbea; review: travados minimizavel e limpeza -> corrigidos). minor: travados modal quando chamado da thread da interface (hoje so via worker)
Polimento pendente (tarefa propria no fim): texto do console 4px a esquerda e 5px acima do CTk em todas as telas (ConsoleFrame/#console)
E4.2: complete (4b95a43, review approved). Desvio a confirmar com Luan: cancelar "Buscar" nao apaga mais a Pasta Raiz.
Polimento pendente: VAO_TEXTO_CAIXA duplicado (dialogs.py usar controles); pmib_manager._marcar_escolhido acumula stylesheet; _texto_dos_avisos copiado do CTk (mover p/ textos_dialogos no corte)
E4.1: complete (b007a7e + fix c7ede7a; review: mono nos dados e botao cinza -> corrigidos)
E4.3: complete (93ed009 + fix 683148d pelo controlador: Esc/Enter/janela unica). minor: barra sempre visivel so no Analyzer -> parametro em area_rolavel se repetir
E3.2: complete (431460a + fix 78e7afd; review: Esc na revisao de PDM, robo solto ao sumir -> corrigidos)
E4.7: complete (0b8921f, review approved)
Polimento pendente: negrito longo ~9% mais largo que o Tk (PDM 291 vs 266; Upload INICIAR 212 vs 202) -- remedir a decisao do 66b4cc5 (sintetico + hinting) em titulos longos
Polimento pendente: radio com largura minima 100 do CTk e altura da aba seguindo a aba selecionada (feitos locais no pdm.py) -> mover p/ estilo/Abas
E4.6: complete (1f0815f, review approved)
Polimento pendente: nome de arquivo longo (>~85 chars) alarga o formulario alem da janela (pdm, pmib_manager, _upload_comum, pickers) -> elidir com QFontMetrics.elidedText num lugar so; _marcar_escolhido acumula stylesheet (pdm, pmib_manager); testes de geometria do PDM com tolerancia em y/h
Polimento pendente: _upload_comum._marcar_escolhido tambem acumula stylesheet
E4.8: complete (a37d43c, review approved). minors: _perguntar duplica perguntar_sim_nao (adicionar padrao_sim ao compartilhado); comentario "1 px por letra" errado; self.automacao nunca limpo (CTk igual, PENDENCIAS)
E5.2: (correcao da 1a linha) integrado como e3ade01, no lote etapa2-en-curso
E4.45: review a137704 (achados em review-e4.45-achados.md): 1 Important (JSON com formato errado some em silencio) + minors 2-8
E4.45: fix round 1 = a7a6858 (worktree aabe14a) -> fc3ee97 em local/jonan-cambios (2026-10-09, retomada); re-review pendente
E4.9: review a2ca532 interrompida na pausa de 2026-10-09 -> retomar o mesmo agente
E4.10: WIP 2c50a79 + nao commitado (worktree ab9f897); implementador ab9f897 interrompido na verificacao final -> retomar
E5.1: WIP so testes (worktree a14a189); implementador a14a189 interrompido -> retomar
E4.45: integrado fc3ee97: check.sh TUDO OK (6126 passed, 27 skipped; 19 warnings pre-existentes em test_autorizados/test_painel/test_pmib_manager_v2), ruff limpo
E6.1: implementador a11a7fe despachado (base fc3ee97, brief-e6.1.md)
E4.9: review a2ca532 concluida (achados em review-e4.9-achados.md): spec ok exceto Important #1 (worker da IA le df_data_selecionado/file_path_pdm vivos: trocar linhas no meio embaralha descricoes x PDMs); minors #2 flag _ia_em_andamento trava "3. Analisar" se a revisao falhar ao abrir, #3 JanelaResumo fechadas se acumulam, #4 quatro rotulos com cinza errado (#E0E0E0 vs gray84), #5 "Concluido" da edicao nao espera; #6a/#6b herdados do CTk (robo com dados nao revisados; segundo robo)
E4.9: fix round 1 -> implementador original a0472fd (base fc3ee97), com #1 + minors #2-#5 + #6a/#6b se pequenos
(2026-10-09 ~21h UTC) limite de sessao da API cortou a16ca8e, a14a189, ab9f897, a11a7fe -> retomados em 2026-10-10
E4.45: fix round 1/5 (7 addressed, 0 open; commits d0590ed..fc3ee97) -- re-review a16ca8e
E4.45: complete (commits af9876f, dcb5e8f, e3fa0f1 + fix fc3ee97; review clean)
E4.45: minor (deferred): dialogs.py com 3 linhas em branco entre sem_tecla e SoltaAoFechar -> polimento
E4.45: minor (deferred, fora do escopo): pmib_manager NovasListasDialog segura o worker e os botoes so tem setAutoDefault(False) (mantem foco) -> aplicar dialogs.sem_tecla no polimento
E4.10: implementador ab9f897 DONE_WITH_CONCERNS: 917db0a -> 354543f em local/jonan-cambios; relatorio e4.10-report.md (copiado do scratchpad: a worktree nao pode gravar aqui)
E4.10: notas p/ LOG: lote processa a fila como estava no clique (itens novos ficam na fila); .txt automatico salvo antes do OK de "Sucesso"; autospec.py em FORA_DO_RECORTE de test_texto_da_ui (textos do Rafael com travessao); AutoSpecCore/IA/web reais nao exercitados
E4.10: minor (deferred): _area_como_a_do_ctk = 4a copia local da area com barra sempre visivel (+ recorte de 6 px) -> parametro em blocos.area_rolavel no polimento
Polimento pendente: botoes de tela pegam foco e Espaco os aperta (CTk nunca dava foco) -> NoFocus no blocos.botao? (todas as telas)
E4.10: review pendente (pacote review-e4.10.diff)
E4.10: integrado 354543f: check.sh TUDO OK (6175 passed, 28 skipped), ruff limpo
E5.1: implementador a14a189 DONE_WITH_CONCERNS: f8dfd08 -> 748d3a4 em local/jonan-cambios; relatorio e5.1-report.md (copiado do scratchpad)
E5.1: notas p/ LOG: "Aplicar mesmo assim?" com padrao Nao (Tk: Sim); MenuDeOpcoes ignora a roda do mouse (como o CTkOptionMenu; vale p/ Busca PMIB e LMR); grade da Home nas posicoes medidas do CTk (cards 438 px); catalogo/pasta de logs/GitHub so com dubles; altura de linha 15 px medida no Linux
E5.1: minor (deferred): _ler_mural, _caminho_do_mapeamento e tabelas do mural copiados do CTk (testes travam os dois lados) -> unificar no corte
E5.1: review ad54afb despachada (pacote review-e5.1.diff)
E4.10: review a47b7fe despachada (pacote review-e4.10.diff)
