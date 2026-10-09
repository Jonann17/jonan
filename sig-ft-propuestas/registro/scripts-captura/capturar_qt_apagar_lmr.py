"""Captura a tela Qt ModuloApagarLMR avulsa (registrada em TELAS só aqui)."""
import sys
from PySide6.QtWidgets import QApplication
from sigft.app import backends
from sigft.app_qt import main as qmain
from sigft.app_qt.views.apagar_lmr import ModuloApagarLMR

saida = sys.argv[1]
qmain.TELAS["ApagarLMR"] = lambda p, c: ModuloApagarLMR(p, c)
qmain._preparar_qt()
backends.carregar_todos()
janela = qmain.SIG_FT_App()
janela.resize(1280, 850)
janela.show()
janela.show_frame("ApagarLMR")
for _ in range(30):
    QApplication.processEvents()
janela.grab().save(f"{saida}/qt_apagar_lmr.png")
t = janela.telas["ApagarLMR"]
def g(w, n, d=0):
    p = w.mapTo(janela, w.rect().topLeft())
    print("  " * d + n, "x", p.x(), "y", p.y(), "w", w.width(), "h", w.height())
g(t, "tela"); g(t.header, "header"); g(t.label_titulo, "titulo"); g(t.content, "content"); g(t.console, "console")
card = t.btn_run.parentWidget(); g(card, "card")
for nome in ("atencao", "irreversivel", "pmib", "opcional"):
    g(t._rotulos[nome], nome, 1)
g(t.entry_pmib, "entry", 1); g(t.picker_status, "picker", 1)
g(t.picker_status.botao, "picker.botao", 2); g(t.picker_status.label_status, "picker.label", 2)
g(t.btn_run, "btn_run", 1); g(t._rotulos["passos"], "passos", 1)
