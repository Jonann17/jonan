import sys, time
from sigft.app import backends
from sigft.app import main as m
saida, tela = sys.argv[1], sys.argv[2]
backends.carregar_todos()
app = m.SIG_FT_App()
app.geometry("1280x850+0+0")
app.show_frame(tela)
for _ in range(30):
    app.update(); time.sleep(0.05)
from PIL import ImageGrab
x, y = app.winfo_rootx(), app.winfo_rooty()
ImageGrab.grab(bbox=(x, y, x + 1280, y + 850)).save(f"{saida}/ctk_{tela}.png")
app.destroy()
