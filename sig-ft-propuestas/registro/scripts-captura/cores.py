import sys
from collections import Counter
from PIL import Image
def cores(arq, caixa, n=3):
    im = Image.open(arq).convert("RGB").crop(caixa)
    return ["#%02X%02X%02X:%d" % (*c, k) for c, k in Counter(im.getdata()).most_common(n)]
ctk = "ctk_apagar_lmr.png"; qt = "qt_apagar_lmr.png"
# (nome, caixa ctk, caixa qt) em coordenadas da janela
itens = [
 ("titulo", (317, 30, 597, 59), (310, 30, 590, 59)),
 ("atencao", (660, 119, 897, 147), (330+355-0, 119, 330+575-20, 147)),
 ("irreversivel", (594, 152, 963, 186), (591, 152, 958, 184)),
 ("entry", (710, 216, 960, 244), (703, 214, 953, 242)),
 ("entry_borda", (710, 228, 713, 232), (703, 226, 706, 230)),
 ("opcional", (583, 269, 974, 299), (584, 267, 966, 297)),
 ("picker_botao", (544, 304, 764, 332), (540, 302, 760, 330)),
 ("picker_label", (779, 304, 997, 332), (775, 302, 995, 330)),
 ("btn_run", (603, 362, 953, 412), (600, 360, 950, 410)),
 ("passos", (648, 432, 909, 507), (646, 430, 907, 505)),
 ("card", (320, 102, 340, 115), (313, 102, 333, 115)),
 ("fundo_tela", (300, 70, 310, 78), (300, 70, 309, 78)),
]
for nome, a, b in itens:
    print(f"{nome:14s} CTK {cores(ctk, a)}\n{'':14s} QT  {cores(qt, b)}")
