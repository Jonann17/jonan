"""Captura a tela CTk ModuloApagarLMR AVULSA (no app ela só existe como aba)."""
import sys, time
from sigft.app import backends
from sigft.app import main as m
from sigft.app.views.apagar_lmr import ModuloApagarLMR
saida = sys.argv[1]
backends.carregar_todos()
app = m.SIG_FT_App()
app.geometry("1280x850+0+0")
app.frames["ApagarLMR"] = ModuloApagarLMR(app.container, app)
app.show_frame("ApagarLMR")
for _ in range(30):
    app.update(); time.sleep(0.05)
from PIL import ImageGrab
x, y = app.winfo_rootx(), app.winfo_rooty()
ImageGrab.grab(bbox=(x, y, x + 1280, y + 850)).save(f"{saida}/ctk_apagar_lmr.png")
f = app.frames["ApagarLMR"]
def g(w, n, d=0):
    print("  " * d + n, "x", w.winfo_rootx()-x, "y", w.winfo_rooty()-y, "w", w.winfo_width(), "h", w.winfo_height())
g(f, "tela"); g(f.header, "header"); g(f.label_titulo, "titulo"); g(f.content, "content"); g(f.console, "console")
def rec(w, d):
    for c in w.winfo_children():
        nome = type(c).__name__
        try: nome += ":" + str(c.cget("text"))[:25].replace("\n", "|")
        except Exception: pass
        if nome.startswith(("CTk", "Linha", "FilePicker")) or d < 2:
            g(c, nome, d)
        rec(c, d + 1)
rec(f.content, 1)
app.destroy()
