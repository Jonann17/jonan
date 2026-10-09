# SDD ledger — plan: /home/user/jonan/sig-ft-propuestas/planos/2026-10-07-qt6-etapa2-pilotos.md
Base da etapa 2: a734d59
Task 1: minor (deferred): TelaComErro empilha a cada visita falha (e um widget meio-montado pode ficar) -- manter um so _tela_erro
Task 1: minor (deferred): teste de traducao deixa o QTranslator instalado no QApplication compartilhado
Task 1: complete (commits a734d59..5ebc911, review clean)
Task 2: minor (deferred): QCheckBox indicator 20px + borda 3px pode virar 26px (CTk = 24px) -- conferir visualmente / usar 18px
Task 2: minor (deferred): QComboBox azul = CTkOptionMenu (nao CTkComboBox); conferir nas telas que usam combo
Task 2: minor (deferred): botoes de QMessageBox ficam azul CTk (provavelmente igual ao Tk nativo); teste nao trava variante primario dos dialogos de espera
Task 2: complete (commits 5ebc911..d620a0e, review clean)
Task 3: minor (deferred): evento.wait() sem timeout em _na_interface_e_esperar (mesmo padrao de _abrir_e_esperar; fechar encerra o processo)
Task 3: minor (deferred): sem teste do caminho "func levanta -> worker solto" e do accept/reject do SelecaoComCaixasDialog
Task 3: minor (deferred): avisar() para widget destruido perde o aviso (so traceback)
Task 3: minor (deferred): SelecaoComCaixasDialog sem botao_confirmar.setDefault(True) -- Enter pode acionar "Todos"; selecionados() vale mesmo apos cancelar (caller deve olhar exec())
Task 3: complete (commits d620a0e..5f19ea5, review clean)
Task 4: minor (deferred): filtro_qt so aceita padrao string (nao tupla); "or cor == COR_BOTAO_SELECAO" em _pintar sem comentario; sem teste de pintar_botao=False (antes de migrar PDM)
Task 4: complete (commits 5f19ea5..d67a42c, review clean)
Task 5: minor (deferred): teste de cor do botao desligado so confere o texto da regra, nao a cor aplicada
Task 5: minor (deferred): altura minima 28 dos rotulos, cor do desligado gray60 e "esquerda"+VCenter so exercitados pelo Tradutor -- conferir nas proximas telas
Task 5: complete (commits d67a42c..691f044, visual fix + review approved; minors 1-3 corrigidos)
Task 6: minor (deferred): avisar() nao bloqueia (CTk: showinfo segurava o navegador aberto ate o OK) -- igual ao Tradutor, aceito
Task 6: minor (deferred): perguntar_sim_nao padrao "Nao" (Tk askyesno: "Sim") -- mais seguro p/ acao destrutiva; registrar no LOG como diferenca intencional
Task 6: minor (deferred): teste de geometria preso as margens do ModuleFrame/cartao (guarda de paridade, aceito)
Task 6: minor -> enviado a rodada de paridade global: QLineEdit global = CTkEntry (28px), tirar o estilo local do campo PMIB
Task 6: complete (commits 691f044..df1f610, review approved)
Paridade global (66b4cc5): review approved. minors deferred: barra lateral AsNeeded perde 10px quando aparece rolagem; hinting so medido no Linux (pedir captura Windows); Roboto-Medium.ttf sem uso mas empacotado; QLineEdit:disabled nao medido
Task 7: minor (deferred): lista de PMIBs sem alternar pelo teclado; "Processo concluido" nao bloqueia (igual Tradutor/Apagar)
Task 7: complete (commits 66b4cc5..9b0da5f + fix 11e574b; review: botao religado durante o robo -> corrigido e conferido pelo controlador)
Task 8: minor (deferred): aplicacao_lmr mexe nas margens do layout raiz da tela embutida (parametro no ModuleFrame seria melhor); dialogo de aba escondida nao troca de aba (igual CTk)
Task 8: complete (11e574b..eda6b3d, review approved)
