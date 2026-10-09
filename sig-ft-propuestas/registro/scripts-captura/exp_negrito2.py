"""Qt vs Tk, por glifo: avanço regular, negrito, e Qt negrito + espaçamento."""
import os, sys
mod = sys.argv[1]
AM = [("Apagar Aplicações LMR", 24), ("ATENÇÃO: AÇÃO DESTRUTIVA", 16), ("Código PMIB:", 14),
      ("INICIAR LIMPEZA", 14), ("  🏠  Home", 13), ("INÍCIO DA FICHA", 11), ("Gestão", 15), ("Abc", 12), ("Abc", 10), ("Abc", 32)]
if mod == "tk":
    import tkinter as tk, tkinter.font as tkf
    r = tk.Tk()
    for t, px in AM:
        n = tkf.Font(family="Roboto", size=-px); b = tkf.Font(family="Roboto", size=-px, weight="bold")
        print(f"{t!r:28}{px:3d}px reg={n.measure(t):4d} neg={b.measure(t):4d} delta/glifo={(b.measure(t)-n.measure(t))/len(t):.2f}")
else:
    from PySide6.QtGui import QFont, QFontDatabase, QFontMetricsF
    from PySide6.QtWidgets import QApplication
    app = QApplication([])
    for a in sys.argv[2:]:
        QFontDatabase.addApplicationFont(os.path.join("/home/user/sig-ft/assets/fonts", a))
    for t, px in AM:
        n = QFont("Roboto"); n.setPixelSize(px)
        b = QFont(n); b.setBold(True)
        s = QFont(b); s.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1)
        w = lambda f: QFontMetricsF(f).horizontalAdvance(t)
        print(f"{t!r:28}{px:3d}px reg={w(n):6.1f} neg={w(b):6.1f} neg+1px={w(s):6.1f} delta/glifo={(w(b)-w(n))/len(t):.2f}")
