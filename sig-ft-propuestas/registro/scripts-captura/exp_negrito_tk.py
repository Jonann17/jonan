"""Tk: mesma coisa, com as faces que estiverem em $HOME/.fonts."""
import tkinter as tk, tkinter.font as tkf
from PIL import ImageGrab
AMOSTRAS = [("Apagar Aplicações LMR", 24), ("ATENÇÃO: AÇÃO DESTRUTIVA", 16),
            ("Código PMIB:", 14), ("INICIAR LIMPEZA", 14), ("Home", 13)]
r = tk.Tk(); r.geometry("+0+0"); r.configure(bg="black")
lbls = []
for texto, px in AMOSTRAS:
    f = tkf.Font(family="Roboto", size=-px, weight="bold")
    l = tk.Label(r, text=texto, font=f, fg="white", bg="black", anchor="w", width=60)
    l.pack(anchor="w"); lbls.append((l, f, texto, px))
for _ in range(10): r.update()
for l, f, texto, px in lbls:
    x, y = l.winfo_rootx(), l.winfo_rooty()
    im = ImageGrab.grab(bbox=(x, y, x + l.winfo_width(), y + l.winfo_height())).convert("L")
    xs = [i for i in range(im.width) for j in range(im.height) if im.getpixel((i, j)) > 100]
    print(f"  {texto!r:28} {px}px  avanço={f.measure(texto):4d}  tinta={max(xs)-min(xs)+1:4d}  actual={f.actual()['family']}")
r.destroy()
