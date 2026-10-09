import os, sys
TAM = (11, 12, 13, 14, 16, 24)
if sys.argv[1] == "tk":
    import tkinter as tk, tkinter.font as tkf
    r = tk.Tk()
    for px in TAM:
        for w in ("normal", "bold"):
            f = tkf.Font(family="Roboto", size=-px, weight=w)
            m = f.metrics()
            print(f"{px:3d} {w:6s} asc={m['ascent']} desc={m['descent']} linespace={m['linespace']} 'Esta ferramenta apaga'={f.measure('Esta ferramenta apaga TODAS as aplicações LMR de uma ficha.')}")
else:
    from PySide6.QtGui import QFont, QFontDatabase, QFontMetrics
    from PySide6.QtWidgets import QApplication
    app = QApplication([])
    QFontDatabase.addApplicationFont("/home/user/sig-ft/assets/fonts/Roboto-Regular.ttf")
    for px in TAM:
        for w in (False, True):
            out = []
            for h in (QFont.HintingPreference.PreferDefaultHinting, QFont.HintingPreference.PreferFullHinting):
                f = QFont("Roboto"); f.setPixelSize(px); f.setBold(w); f.setHintingPreference(h)
                m = QFontMetrics(f)
                out.append(f"asc={m.ascent()} desc={m.descent()} lineSpacing={m.lineSpacing()} larg={m.horizontalAdvance('Esta ferramenta apaga TODAS as aplicações LMR de uma ficha.')}")
            print(f"{px:3d} {'bold' if w else 'normal':6s} padrão[{out[0]}]  completo[{out[1]}]")
