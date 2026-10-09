"""Qt: largura de tinta de textos em negrito, com o conjunto de faces passado."""
import os, sys
from PySide6.QtGui import QFont, QFontDatabase, QFontInfo, QFontMetrics, QImage, QPainter, QColor
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
PASTA = "/home/user/sig-ft/assets/fonts"
AMOSTRAS = [("Apagar Aplicações LMR", 24), ("ATENÇÃO: AÇÃO DESTRUTIVA", 16),
            ("Código PMIB:", 14), ("INICIAR LIMPEZA", 14), ("Home", 13)]
app = QApplication(sys.argv[:1])
arquivos = sys.argv[1:]
for a in arquivos:
    QFontDatabase.addApplicationFont(os.path.join(PASTA, a))
print("faces:", arquivos, "| estilos Roboto:", QFontDatabase.styles("Roboto"))
for texto, px in AMOSTRAS:
    f = QFont("Roboto"); f.setPixelSize(px); f.setBold(True)
    info = QFontInfo(f)
    img = QImage(800, 60, QImage.Format.Format_RGB32); img.fill(QColor("black"))
    p = QPainter(img); p.setFont(f); p.setPen(QColor("white")); p.drawText(10, 45, texto); p.end()
    xs = [x for x in range(800) for y in range(60) if QColor(img.pixel(x, y)).red() > 100]
    print(f"  {texto!r:28} {px}px  avanço={QFontMetrics(f).horizontalAdvance(texto):4d}"
          f"  tinta={max(xs)-min(xs)+1:4d}  face={info.family()}/{info.styleName()} peso={info.weight()}")
