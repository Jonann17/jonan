import sys, time
from sigft.app import backends
from sigft.app import main as m
backends.carregar_todos()
app = m.SIG_FT_App()
app.geometry("1280x850+0+0")
app.show_frame("Translator")
for _ in range(30):
    app.update(); time.sleep(0.05)
f = app.frames["Translator"]
def g(w, n):
    print(n, "x", w.winfo_rootx()-app.winfo_rootx(), "y", w.winfo_rooty()-app.winfo_rooty(), "w", w.winfo_width(), "h", w.winfo_height())
g(f, "tela"); g(f.header, "header"); g(f.label_titulo, "titulo"); g(f.content, "content"); g(f.console, "console")
for c in f.content.winfo_children():
    g(c, "card")
    for cc in c.winfo_children():
        if hasattr(cc, "cget"):
            try: g(cc, type(cc).__name__+":"+str(cc.cget("text"))[:20])
            except Exception: pass
print(f.label_titulo._font if hasattr(f.label_titulo, "_font") else "")
app.destroy()
