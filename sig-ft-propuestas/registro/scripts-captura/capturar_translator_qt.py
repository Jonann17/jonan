import sys
from PySide6.QtWidgets import QApplication
from sigft.app import backends
from sigft.app_qt import main as qmain
from sigft.app_qt.views.translator import ModuloTranslator

saida = sys.argv[1]
qmain._preparar_qt()
backends.carregar_todos()
janela = qmain.SIG_FT_App()
janela.resize(1280, 850)
janela.show()
tela = ModuloTranslator(janela.pilha, janela)
janela.pilha.addWidget(tela)
janela.pilha.setCurrentWidget(tela)
tela.log("Exemplo de linha de log.")
for _ in range(20):
    QApplication.processEvents()
janela.grab().save(f"{saida}/qt_translator.png")
print("ok", backends.falhas)
