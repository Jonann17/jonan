# SDD ledger — plan: /home/user/jonan/sig-ft-propuestas/planos/2026-10-07-qt6-etapa1-base.md
Task 1: minor (deferred): conftest.py `import os as _os_qt` duplica `import os` (prescrito pelo plano)
Task 1: minor (deferred): ci.yml compileall sem -x .venv (seguro hoje no CI)
Task 1: complete (commits 4712025..ddafd2e, review clean)
Task 2: minor (deferred): guarda de sintaxe antiga cobre so python_minimo.py, nao sigft/__init__.py, sigft/core/__init__.py, sigft/_build_info.py
Task 2: minor (deferred): trailer Co-Authored-By diz Haiku 5.5 (modelo do subagente) em vez de Opus 5.5
Task 2: minor (deferred): abrir `python frontend.py` com tkinter ainda devido (fazer na Task 11/12 com python3.12+xvfb)
Task 2: complete (commits ddafd2e..26a4e5c, review clean)
Task 3: minor (deferred): U+FE0E literal invisivel em estilo.py e no teste (preferir escape)
Task 3: minor (deferred): QSS com cinzas estruturais em hex (#3A3A3A, #333333...) nao conferidos um a um contra a UI atual
Task 3: fix round 1/5 (1 addressed, 0 open — cinza_tk tabela X11 literal; commits 74fada2..754deb9)
Task 3: complete (commits 26a4e5c..754deb9, review clean)
Task 4: minor (deferred): instalar() nao documenta/guarda que deve rodar na thread da interface (opcional: checar QThread.currentThread())
Task 4: minor (deferred): trailer Co-Authored-By com modelo do subagente
Task 4: complete (commits 754deb9..39025ab, review clean)
Task 5: minor (deferred): exigir() aceita qualquer nome global e typo vira "ainda nao foi carregado" (sem guarda de nome valido)
Task 5: minor (deferred): falhas nunca e limpo se carregar_todos rodar de novo
Task 5: fix round 1/5 (1 addressed, 0 open — falhas tambem por nome de classe em mixed_classes; commits e76b0b6..252c065)
Task 5: minor (deferred): mensagem de exigir() nao nomeia o modulo Python que falhou (so aparece se o erro trouxer o nome)
Task 5: complete (commits 39025ab..252c065, review clean)
Achado fora de escopo (para o LOG/Luan): tests/test_llm_comparacao.py:408 faz os.chdir(tmp_path) sem restaurar (deveria ser monkeypatch.chdir) -- testes que usam caminho relativo ao cwd falham conforme a ordem. Task 9 deve resolver caminhos por __file__.
Task 6: minor (deferred): console.log nao reseta _agendado se na_interface levantar RuntimeError (console fica mudo; so em teardown/erro de programacao)
Task 6: minor (deferred): console sempre rola para o fim mesmo se a pessoa subiu a barra (UX futuro)
Task 6: minor (deferred): teste de widget destruido e so smoke (nao prova o ramo except)
Task 6: complete (commits 252c065..094d068, review clean)
Task 7: minor (deferred): dialogos fechados nunca sao destruidos (sem WA_DeleteOnClose); _dialogo_aberto redundante (parent ja mantem vivo)
Task 7: minor (deferred): caminho exec() na thread da interface sem teste
Task 7: minor (deferred): no caminho do worker o dialogo e nao-modal (igual a UI atual, sem grab_set)
Task 7: fix round 1/5 (2 addressed, 0 open — Esc solta worker via reject(); falha de construcao solta worker; commits f5fdba9..952522a)
Task 7: complete (commits 094d068..952522a, review clean)
Task 8: minor (deferred): iniciar_tarefa reabilita botao destruido -> traceback no stderr (conter RuntimeError como o console faz)
Task 8: minor (deferred): backend() sem guarda de thread (QMessageBox fora da thread da interface derruba no macOS) -- importante para as telas das etapas 2-5
Task 8: minor (deferred): altura_console=None da stretch 1 ao console (no CTk so o conteudo esticava) -- revisar ao migrar as 5 telas sem altura
Task 8: minor (deferred): parametros CTk sem equivalente (console_sticky, console_pady, largura/altura/cor_progresso); scroll embutido sem estilo; header QVBox em vez de QHBox; import pytest sem uso
Task 8: complete (commits 952522a..7e75724, review clean)
Task 9: minor (deferred): MENU (rotulos e secoes) nao travado por AST contra main.py; open() sem with no teste
Task 9: complete (commits 7e75724..fbdeea5, review clean)
Task 10: minor (deferred): teste de clique so no margem do card (nao prova labels transparentes); navega no press e nao aceita o evento (QTest avisa "MousePress not accepted"); nome do painel extraido por split('  ')
Task 10: complete (commits fbdeea5..1aa811c, review clean)
Controller: frontend.py (CTk) abriu sob xvfb com venv312 apos a Task 2 (exit 124 = continuou aberto) -- pendencia da Task 2 resolvida. App Qt real: capturas qt_home.png e qt_nao_migrada.png conferidas (iguais ao prototipo v2).
Task 11: minor (deferred): QMessageBox.critical de abertura falha aparece com a splash ainda visivel (esconder a splash antes)
Task 11: minor (deferred): save_keys deixa .tmp para tras se json.dump/os.replace falhar; sem fsync
Task 11: minor (deferred): ramos Yes/sem-tarefa do closeEvent e caminho 1 do --smoke sem teste; handoff splash->janela sem teste
Task 11: deferred to Etapa 6 (empacotamento): --smoke Qt deve gravar relatorio com conferencia.gravar_relatorio(ARQUIVO_JANELA, ...) como o smoke CTk (console=False no .exe)
Task 11: fix round 1/5 (2 addressed, 0 open — splash sempre emite pronta; --smoke relata backend que falhou; commits 1714cca..84a4f43)
Task 11: complete (commits 1aa811c..84a4f43, review clean)
FINAL REVIEW (opus, 3395788..84a4f43): ready with fixes. C1 ruff F401; C2 PySide6 em requirements.txt quebra SIG-FT.bat; I1 .spec coleta app_qt/PySide6; I2 backend() fora da thread; I3 _smoke trava com thread nao-daemon; I4 main() Qt sem .env/migracao/RPA/log; I5 telas Qt importam tkinter via sigft.app.widgets.dialogs. Minors incluidos na onda: FE0E literal, mono() emojis faltando + FE0F, check.sh venv/.
Controller ruling: trailers Co-Authored-By com o modelo real de cada subagente (Haiku) ficam como estao -- reescrever para outro modelo seria atribuicao falsa. Nao reescrever historico.
Final fix wave: commits 84a4f43..a734d59 (9 commits), re-review: all findings addressed (C1,C2,I1-I5,M1-M3).
Task 12: medicao smoke (xvfb, venv312, 3 rodadas): CTk 3,99/3,75/3,71 s (mediana 3,75); Qt 3,34/2,98/3,35 s (mediana 3,34) -> ~0,4 s (~11%) mais rapido, sem contar ~1,9 s de pausas artificiais removidas da splash.
