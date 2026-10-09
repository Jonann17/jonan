import sys
from PySide6.QtWidgets import QApplication
from sigft.app import backends
from sigft.app_qt import main as qmain
from sigft.app_qt.views.translator import ModuloTranslator

saida = sys.argv[1]
qmain.TELAS["Translator"] = lambda p, c: ModuloTranslator(p, c)
qmain._preparar_qt()
backends.carregar_todos()
janela = qmain.SIG_FT_App()
janela.resize(1280, 850)
janela.show()
janela.show_frame("Translator")
for _ in range(30):
    QApplication.processEvents()
janela.grab().save(f"{saida}/qt_translator.png")
t = janela.telas["Translator"]
def g(w, n):
    p = w.mapTo(janela, w.rect().topLeft())
    print(n, "x", p.x(), "y", p.y(), "w", w.width(), "h", w.height())
g(t, "tela"); g(t.header, "header"); g(t.label_titulo, "titulo"); g(t.content, "content"); g(t.console, "console")
card = t.btn_run.parentWidget(); g(card, "card")
for w in card.findChildren(object):
    if hasattr(w, "text") and hasattr(w, "mapTo"):
        g(w, type(w).__name__ + ":" + w.text()[:20])
