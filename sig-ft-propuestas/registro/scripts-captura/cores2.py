import sys
sys.argv = sys.argv[:1]
exec(open(sys.path[0] + "/cores.py").read().split("for nome, a, b")[0])
from PIL import Image
def nucleo(arq, caixa):
    im = Image.open(arq).convert("RGB").crop(caixa)
    px = list(im.get_flattened_data()) if hasattr(im, "get_flattened_data") else list(im.getdata())
    fundo = Counter(px).most_common(1)[0][0]
    longe = max(px, key=lambda c: sum(abs(a - b) for a, b in zip(c, fundo)))
    return "#%02X%02X%02X" % longe
for nome, a, b in itens:
    print(f"{nome:14s} CTK {nucleo(ctk, a)}  QT {nucleo(qt, b)}")
