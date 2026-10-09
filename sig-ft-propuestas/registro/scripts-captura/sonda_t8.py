from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QColor
app = QApplication([])
from sigft.app_qt import estilo
app.setStyleSheet(estilo.folha_de_estilo())
from sigft.app_qt.views.aplicacao_lmr import ModuloAplicacaoLMR
t = ModuloAplicacaoLMR(); t.resize(1003, 850); t.show()
for _ in range(20): app.processEvents()
im = t.grab().toImage()
for y in range(79, 135):
    linha = [QColor(im.pixel(x, y)).name() for x in (45, 300, 500, 945, 960)]
    print(y, linha)
fundo = QColor("#212121").rgb()
for y in range(116, 131):
    xs = [x for x in range(40, 963) if im.pixel(x, y) != fundo]
    if xs: print("nao-fundo", y, xs[:5], xs[-5:], QColor(im.pixel(xs[0], y)).name())
vp = t.tela_upload.content.parentWidget()
print("vp", vp.mapTo(t, vp.rect().topLeft()), vp.size(), type(vp.parentWidget()).__name__)
