import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
sys.path.insert(0, "/home/user/sig-ft")
app = QApplication([])
from sigft.app_qt import estilo
from sigft.app_qt.widgets import blocos
from sigft.app import theme
app.setStyleSheet(estilo.folha_de_estilo())
w = QWidget(); lay = QVBoxLayout(w)
area, lista = blocos.area_rolavel(cor=theme.COR_CARTAO)
lay.addWidget(area)
b1 = blocos.botao("Abrir", variante="cinza", largura=120, altura=28)
b2 = blocos.botao("Abrir", largura=120, altura=28, cor_fundo="#3A3A3A", cor_hover="#454545")
lista.addWidget(b1); lista.addWidget(b2)
w.resize(400,300); w.show(); app.processEvents()
for b in (b1,b2):
    img = b.grab().toImage(); print(img.pixelColor(5, 14).name(), b.styleSheet())
