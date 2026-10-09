import sys
from PySide6.QtWidgets import QApplication
from sigft.app import backends
from sigft.app_qt import main as qmain

saida = sys.argv[1]
qmain._preparar_qt()
backends.carregar_todos()
janela = qmain.SIG_FT_App()
janela.resize(1280, 850)
janela.show()
for _ in range(20):
    QApplication.processEvents()
janela.grab().save(f"{saida}/qt_home.png")
janela.show_frame("Analyzer")
for _ in range(10):
    QApplication.processEvents()
janela.grab().save(f"{saida}/qt_nao_migrada.png")
print("falhas:", backends.falhas)
