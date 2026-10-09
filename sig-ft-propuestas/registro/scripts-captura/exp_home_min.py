from PySide6.QtWidgets import QApplication
from sigft.app_qt import estilo
from sigft.app_qt.views.home import HomeView
class C:
    def show_frame(self, n): pass
app = QApplication([])
estilo.carregar_fontes()
app.setStyleSheet(estilo.folha_de_estilo())
h = HomeView(controller=C()); h.resize(1003, 850); h.show(); app.processEvents()
corpo = h.widget()
print("viewport", h.viewport().width(), "corpo min", corpo.minimumSizeHint().width(), "corpo w", corpo.width(), "hbar", h.horizontalScrollBar().isVisible(), h.horizontalScrollBar().maximum())
print("margens", corpo.layout().contentsMargins())
lay = corpo.layout()
for i in range(lay.count()):
    it = lay.itemAt(i)
    w = it.widget() or it.layout()
    print(i, type(w).__name__, it.minimumSize().width(), it.sizeHint().width())
print([ (b.width(), b.minimumSizeHint().width()) for b in h.botoes_barra.values()], h.caixa_canal_testes.minimumSizeHint().width())
