import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
from sigft.app_qt import estilo
app = QApplication(sys.argv)
app.setStyleSheet(estilo.folha_de_estilo())
w = QWidget(); l = QVBoxLayout(w)
res = []
for var in (None, "contorno"):
    for modo in ("zero", "auto"):
        b = QPushButton("x")
        if var: b.setProperty("variante", var)
        b.setStyleSheet("min-height: 0px;" if modo=="zero" else "min-height: auto; max-height: auto;")
        b.setFixedHeight(50)
        l.addWidget(b); res.append((var, modo, b))
w.show(); app.processEvents()
for var, modo, b in res:
    print(var, modo, b.height(), b.sizeHint().height(), b.minimumHeight(), b.maximumHeight())
