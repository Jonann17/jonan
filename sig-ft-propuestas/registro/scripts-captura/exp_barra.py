from PySide6.QtGui import QFontMetrics
from PySide6.QtWidgets import QApplication, QPushButton, QWidget, QHBoxLayout
from sigft.app_qt import estilo
from sigft.app_qt.views import home
app = QApplication([])
estilo.carregar_fontes()
app.setStyleSheet(estilo.folha_de_estilo())
for regra in ("", "QPushButton[barra=\"true\"] { padding: 0 7px; min-width: 126px; }"):
    w = QWidget(); w.setStyleSheet(regra); lay = QHBoxLayout(w)
    bs = []
    for _c, texto, var in home.BARRA:
        b = QPushButton(estilo.mono(texto)); b.setProperty("barra", True)
        if var: b.setProperty("variante", var)
        lay.addWidget(b); bs.append(b)
    w.show(); app.processEvents()
    print(repr(regra[:40]), [(b.text()[-12:], b.width(), QFontMetrics(b.font()).horizontalAdvance(b.text())) for b in bs])
