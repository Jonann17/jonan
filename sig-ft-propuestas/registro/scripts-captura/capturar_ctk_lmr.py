"""Captura a tela CTk ModuloLMR AVULSA, a aba Upload da Aplicação LMR e os dois diálogos."""
import sys, time
from sigft.app import backends
from sigft.app import main as m
from sigft.app.views.lmr import ModuloLMR
from PIL import ImageGrab
saida = sys.argv[1]
backends.carregar_todos()
app = m.SIG_FT_App()
app.geometry("1280x850+0+0")
app.frames["LMRAvulsa"] = ModuloLMR(app.container, app)

def esperar(n=30):
    for _ in range(n):
        app.update(); time.sleep(0.05)

x, y = 0, 0
def g(w, n, d=0):
    print("  " * d + n, "x", w.winfo_rootx()-x, "y", w.winfo_rooty()-y, "w", w.winfo_width(), "h", w.winfo_height())
def rec(w, d):
    for c in w.winfo_children():
        nome = type(c).__name__
        try: nome += ":" + str(c.cget("text"))[:25].replace("\n", "|")
        except Exception: pass
        if nome.startswith(("CTk", "Linha", "FilePicker", "Label")) or d < 2:
            g(c, nome, d)
        rec(c, d + 1)

# 1. aba Upload dentro da seção (como o app mostra)
app.show_frame("LMR"); esperar()
x, y = app.winfo_rootx(), app.winfo_rooty()
ImageGrab.grab(bbox=(x, y, x + 1280, y + 850)).save(f"{saida}/ctk_aplicacao_lmr_upload.png")
# 2. avulsa
app.show_frame("LMRAvulsa"); esperar()
ImageGrab.grab(bbox=(x, y, x + 1280, y + 850)).save(f"{saida}/ctk_lmr.png")
f = app.frames["LMRAvulsa"]
print("== tela avulsa")
g(f, "tela"); g(f.header, "header"); g(f.label_titulo, "titulo"); g(f.content, "content"); g(f.console, "console")
rec(f.content, 1)
# 2b. interruptor ligado
f.var_linha_inicial.set(True)
f.entry_linha_inicial.configure(state="normal")
f.entry_linha_inicial.insert(0, "12")
esperar(10)
ImageGrab.grab(bbox=(x, y, x + 1280, y + 850)).save(f"{saida}/ctk_lmr_ligado.png")
# 3. diálogo da aba
f._escolher_aba_lmr("/tmp/LMR_Aplicacoes_2026.xlsx", ["Plan1", "LMR", "GERAL"])
esperar(20)
top = [w for w in f.winfo_children() if type(w).__name__ == "CTkToplevel"][-1]
tx, ty = top.winfo_rootx(), top.winfo_rooty()
ImageGrab.grab(bbox=(tx, ty, tx + top.winfo_width(), ty + top.winfo_height())).save(f"{saida}/ctk_dialogo_aba.png")
print("== dialogo aba", top.winfo_width(), top.winfo_height())
x, y = tx, ty
rec(top, 1)
top.destroy()
# 4. diálogo de PMIBs
x, y = app.winfo_rootx(), app.winfo_rooty()
pmibs = [f"4500063671.{i:04d}" for i in range(1, 31)]
f._janela_selecao_pmib(pmibs, None)
esperar(20)
top = [w for w in f.winfo_children() if type(w).__name__ == "CTkToplevel"][-1]
# marca duas
caixas = []
def achar(w):
    for c in w.winfo_children():
        if type(c).__name__ == "CTkCheckBox": caixas.append(c)
        achar(c)
achar(top)
caixas[1].select(); caixas[3].select()
esperar(10)
tx, ty = top.winfo_rootx(), top.winfo_rooty()
ImageGrab.grab(bbox=(tx, ty, tx + top.winfo_width(), ty + top.winfo_height())).save(f"{saida}/ctk_dialogo_pmibs.png")
print("== dialogo pmibs", top.winfo_width(), top.winfo_height())
x, y = tx, ty
rec(top, 1)
top.destroy()
app.destroy()
