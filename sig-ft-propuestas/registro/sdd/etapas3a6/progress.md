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
