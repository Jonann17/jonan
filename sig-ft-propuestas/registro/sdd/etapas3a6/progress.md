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
E5.1: integrado 748d3a4: check.sh TUDO OK (6250 passed, 28 skipped; warnings so as pre-existentes), ruff limpo
E4.10: review a47b7fe (achados em review-e4.10-achados.md): Important #1 titulo de link com "&" vira mnemonico (some o "&" e pega atalho Alt); #2 PROCESSAR religa no meio da 2a passada (IMPORTAR) -> duas passadas concorrentes
E4.10: minor (deferred): #3 bloco de folha da barra sempre visivel copiado em autospec/copia_fichas/cria_fichas (polimento); #4 herdado: fim de lote substitui conferencia importada com marcas nao salvas (Nota p/ Rafael / PENDENCIAS); #7 Espaco aperta botao com foco (polimento); nits: alias FAMILIAS_COM_SIMBOLO em cria_fichas:79 e font-family repetido (polimento)
E4.10: fix round 1 -> implementador ab9f897 (base 748d3a4): #1, #2 + minors #1 (ERRO FATAL no fim do lote), #2 (corrigir descricao da fila no relatorio/teste), #5 (waitUntil), #6 (teste do X no lote), nit controles:178
(2026-10-10 ~06h UTC) limite de sessao cortou ab9f897 (fix E4.10), ad54afb (review E5.1), a0472fd (fix E4.9), a11a7fe (E6.1) -> retomados 11:51 UTC; E4.9 e E6.1 instruidos a rebasear em 748d3a4
E4.9: fix round 1 implementado: 4530a3a (rebaseado em 748d3a4; ff em local/jonan-cambios); check.sh do agente no mesmo commit: TUDO OK (6255 passed, 28 skipped), ruff limpo; re-review pendente (review-e4.9-fix1.diff)
E4.9: notas p/ LOG: self.catalogo muda so quando a revisao e confirmada (junto com df_processed); robos de criacao e de edicao nao rodam juntos (motivo no console)
E4.9: p/ Luan (herdado do CTk, PENDENCIAS): "4. Robo Web" continua ligado com o mesmo lote no fim -> segundo clique cria as mesmas fichas de novo; "Limpar" durante o robo religa "4. Robo Web" sem dados (abre navegador e falha)
E5.1: review ad54afb (achados em review-e5.1-achados.md): spec ok (cards compactos mantidos, 12 cards sem rolar: 815 <= 850); Important #1 _ler_mural/_caminho_do_mapeamento copiados linha a linha na view Qt sem teste de sincronia (regra de negocio na UI)
E5.1: minor (deferred): #4 home.py com 1162 linhas e _rotulo quase duplicado (home.py:126 x mural.py:84) -> polimento
E5.1: fix round 1 -> implementador a14a189 (base 4530a3a): Important #1 (extrair p/ modulo sem tkinter, CTk delega) + minors #1 mural com PlainText (dado do usuario), #2 lacunas de teste, #3 restaurar sem desmaximizar
E4.10: fix round 1 implementado: 2b562ad -> ab74059 em local/jonan-cambios (check.sh do agente em 748d3a4+fix: TUDO OK 6256/28); extra 1b: rotulos com dado do usuario em PlainText; re-review pendente (review-e4.10-fix1.diff)
E6.1: implementador a11a7fe DONE_WITH_CONCERNS: 7febd4e (rebaseado em 748d3a4); check.sh do agente TUDO OK (6293/28); aberturas reais: frontend.py=Qt (sem Tk), --ctk=CTk (sem Qt), --smoke grava relatorio (12 telas); relatorio e6.1-report.md (copiado)
E6.1: notas p/ LOG: nao lancar Release antes da E6.2 (spec ainda exclui PySide6 -> conferir-pacote reprova); lancador macOS nao rodou num Mac; SIG-FT.bat nao repassa argumentos (--ctk so via python frontend.py --ctk); tela nova em TELAS exige o modulo em MODULOS_ESSENCIAIS (teste avisa)
E6.1: review despachada (pacote review-e6.1.diff; cherry-pick depois da suite de ab74059)
E4.9+E4.10 fixes: integrado ab74059: check.sh TUDO OK (6261 passed, 28 skipped), ruff limpo
E6.1: integrado 7febd4e -> 61bf09f em local/jonan-cambios (suite rodando); review a376e8c em andamento
E6.2: implementador ac41efc despachado (base 61bf09f, brief-e6.2.md)
E4.9: fix round 1/5 (7 addressed, 1 open: NOVO Important -- "4. Robo Web" fica desligado para sempre se a revisao e confirmada com o robo de EDICAO rodando; commits 748d3a4..4530a3a; re-review af1a448 em rereview-e4.9-r1.md)
E4.9: fix round 2 -> implementador a0472fd (base 61bf09f): _robo_terminou devolve btn_run_auto se df_processed existe + teste; opcional no mesmo commit: Limpar zera catalogo (observacao fora do escopo), nit teste :565-568
E4.10: fix round 1/5 (8 addressed, 0 open; commits 4530a3a..ab74059) -- re-review ac9cfa1
E4.10: complete (commits 354543f + fix ab74059; review clean)
E4.10: minor (deferred): linha velha no e4.10-report.md:257 (fim de lote "religa PROCESSAR") ficou falsa -> corrigir no relatorio; herdado do CTk: lote x 2a passada gravam o mesmo {ficha}_completed (services/autospec.py:3487-3493, :3781) -> PENDENCIAS / Nota p/ Rafael
E6.1: integrado 61bf09f: check.sh TUDO OK (6304 passed, 28 skipped), ruff limpo
E6.1: smoke real no ramo integrado (61bf09f, frontend.py --smoke offscreen): exit 0, 12 telas OK, CorrecaoPDM bloqueada nao visitada; relatorio gravado
(2026-10-10 ~13h UTC) limite de sessao cortou a0472fd (fix2 E4.9, inicio), a376e8c (review E6.1, meio), a14a189 (fix1 E5.1, quase no fim: relatorio), ac41efc (E6.2, meio: licencas) -> reset 16:50 UTC
E5.1: fix round 1 implementado: c0cdc5c -> 4069f7c em local/jonan-cambios (check.sh do agente em 4530a3a+fix: TUDO OK 6264/28); servico novo sigft/services/mural_atividades.py (atividades.py e travado contra openpyxl); re-review pendente (review-e5.1-fix1.diff)
E6.1: review a376e8c: Approved (spec ok, sem Critical/Important; achados em review-e6.1-achados.md)
E6.1: complete (commits 7febd4e -> 61bf09f; review clean)
E6.1: minor (deferred -> rodada de melhorias com a11a7fe): #1 PySide6 ausente/quebrado nao leva ao --ctk; #2 falha no import da Qt com --smoke nao grava relatorio (Release pendura); #3 iCloud: tratar Desktop/Documents como sincronizados; #4 .gitattributes eol=lf p/ *.sh e *.command; #5 nits de teste; #6 nao gerar .exe antes da E6.2; #7 ruido pre-existente
E6.1: rodada de melhorias (minors 1-5) -> a11a7fe (base 4069f7c); decisao do controlador p/ #1: sem --smoke, falha da Qt mostra mensagem e cai na CTk no mesmo processo; com --smoke grava relatorio e sai 1; E6.2 (ac41efc) avisado p/ conferencia carregar a Qt de verdade
E5.1 fix: integrado 4069f7c: check.sh TUDO OK (6313 passed, 28 skipped), ruff limpo
E4.9: fix round 2 implementado: 664e40e -> 11ed015 (check.sh do agente em 61bf09f+fix: TUDO OK 6306/28); desvio novo: depois do Limpar, revisao do Pular IA abre com editor livre; re-review pendente (review-e4.9-fix2.diff)
E5.1: fix round 1/5 (4 addressed, 0 open; commits 61bf09f..4069f7c) -- re-review ac8cf12
E5.1: complete (commits 748d3a4 + fix 4069f7c; review clean)
E5.1: minor (deferred -> polimento): test_as_homes_nao_leem_a_planilha contornavel (from openpyxl import ...); docstring de views/home.py sem mural_atividades; mural_atividades fora do test_qt_sem_tkinter; test_le_as_colunas_e_classifica preenche 5 de 10 colunas; os.listdir fora do try em mural_atividades (herdado, PermissionError escapa do botao)
E4.9 fix2: integrado 11ed015: check.sh TUDO OK (6315 passed, 28 skipped), ruff limpo
E4.9: fix round 2/5 (1 addressed + 2 opcionais, 0 open; commits 4069f7c..11ed015) -- re-review ae9d9d5
E4.9: complete (commits 9838d2f + fixes 4530a3a, 11ed015; review clean)
E4.9: p/ Luan (herdado do CTk, PENDENCIAS): no fim do robo de CRIACAO, iniciar_tarefa religa "4. Robo Web" mesmo sem lote (Limpar com o robo rodando)
POLIMENTO: implementador despachado (base 11ed015, brief-polimento.md)
