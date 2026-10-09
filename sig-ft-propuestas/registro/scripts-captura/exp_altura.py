import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
from sigft.app_qt import estilo
app = QApplication(sys.argv)
app.setStyleSheet(estilo.folha_de_estilo())
w = QWidget(); l = QVBoxLayout(w)
res = []
for var in (None, "primario", "contorno", "perigo"):
    for modo in ("fixed", "qss", "qss_box"):
        b = QPushButton("x")
        if var: b.setProperty("variante", var)
        if modo == "fixed":
            b.setFixedHeight(50)
        elif modo == "qss":
            b.setStyleSheet("min-height: 50px; max-height: 50px;")
        else:
            b.setStyleSheet("min-height: 48px; max-height: 48px;")
        l.addWidget(b); res.append((var, modo, b))
w.show(); app.processEvents()
for var, modo, b in res:
    print(var, modo, b.height(), b.sizeHint().height(), b.minimumHeight(), b.maximumHeight())
