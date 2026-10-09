import sys
from PySide6.QtWidgets import QApplication
from sigft.app import backends
from sigft.app_qt import catalogo, main as qmain
from sigft.app_qt.views.nao_migrada import TelaComErro, TelaNaoMigrada

saida = sys.argv[1]
qmain._preparar_qt()
backends.carregar_todos()
print("backends que nao carregaram:", sorted(backends.falhas))
janela = qmain.SIG_FT_App()
janela.resize(1280, 850)
janela.show()
for _ in range(20):
    QApplication.processEvents()
for tipo, *resto in catalogo.MENU:
    if tipo != "botao":
        continue
    texto, chave = resto
    if chave in catalogo.TELAS_BLOQUEADAS:
        print(f"{chave:18s} BLOQUEADA (botao habilitado={janela.botoes_menu[chave].isEnabled()})")
        continue
    janela.botoes_menu[chave].click()
    for _ in range(30):
        QApplication.processEvents()
    tela = janela.pilha.currentWidget()
    estado = ("NAO MIGRADA" if isinstance(tela, TelaNaoMigrada)
              else "ERRO" if isinstance(tela, TelaComErro) else "ok")
    print(f"{chave:18s} {type(tela).__name__:26s} {estado}")
    janela.grab().save(f"{saida}/{chave}.png")
janela.show_home()
for _ in range(20):
    QApplication.processEvents()
janela.grab().save(f"{saida}/Home.png")
