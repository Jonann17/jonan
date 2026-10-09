import os, sys
from PySide6.QtGui import QFont, QFontDatabase, QFontMetricsF
from PySide6.QtWidgets import QApplication
AM = [("Apagar Aplicações LMR", 24), ("ATENÇÃO: AÇÃO DESTRUTIVA", 16), ("Código PMIB:", 14),
      ("INICIAR LIMPEZA", 14), ("  🏠  Home", 13), ("INÍCIO DA FICHA", 11), ("Gestão", 15), ("Abc", 12), ("Abc", 10), ("Abc", 32)]
app = QApplication([])
for a in sys.argv[1:]:
    QFontDatabase.addApplicationFont(os.path.join("/home/user/sig-ft/assets/fonts", a))
for t, px in AM:
    out = []
    for h in (QFont.HintingPreference.PreferDefaultHinting, QFont.HintingPreference.PreferFullHinting):
        n = QFont("Roboto"); n.setPixelSize(px); n.setHintingPreference(h)
        b = QFont(n); b.setBold(True)
        out.append(f"reg={QFontMetricsF(n).horizontalAdvance(t):6.1f} neg={QFontMetricsF(b).horizontalAdvance(t):6.1f}")
    print(f"{t!r:28}{px:3d}px padrão: {out[0]} | completo: {out[1]}")
