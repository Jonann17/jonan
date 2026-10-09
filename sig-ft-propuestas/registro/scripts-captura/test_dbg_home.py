from sigft.app_qt import estilo
from sigft.app_qt.views.home import HomeView
class C:
    def show_frame(self, n): pass
def test_dbg(qt_interface, qtbot):
    qt_interface.setStyleSheet(estilo.folha_de_estilo())
    estilo.carregar_fontes()
    h = HomeView(controller=C()); qtbot.addWidget(h); h.resize(1003, 850); h.show(); qtbot.waitExposed(h)
    corpo = h.widget()
    print("\nvis", h.horizontalScrollBar().isVisible(), h.verticalScrollBar().isVisible(), "viewport", h.viewport().width(), "corpo min", corpo.minimumSizeHint().width(), "hbar", h.horizontalScrollBar().maximum())
    lay = corpo.layout()
    for i in range(lay.count()):
        it = lay.itemAt(i); print(i, it.minimumSize().width(), it.sizeHint().width())
    print([(b.width(), b.text()) for b in h.botoes_barra.values()], h.caixa_canal_testes.minimumSizeHint().width(), h.caixa_canal_testes.font().family())
    for k, c in h.cards.items():
        print(k, c.minimumSizeHint().width())
