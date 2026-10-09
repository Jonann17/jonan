"""Caixas de 'tinta' (pixels diferentes do fundo do cartão) por faixa de linhas."""
import sys
from PIL import Image
def faixas(arq, card):  # card = (x0, y0, x1, y1)
    im = Image.open(arq).convert("RGB")
    x0, y0, x1, y1 = card
    fundo = im.getpixel((x0 + 3, y0 + 12))
    linhas = []
    for y in range(y0 + 10, y1 - 10):
        xs = [x for x in range(x0 + 10, x1 - 10) if sum(abs(a - b) for a, b in zip(im.getpixel((x, y)), fundo)) > 40]
        linhas.append((y, xs))
    out, atual = [], None
    for y, xs in linhas:
        if xs:
            if atual is None: atual = [y, y, min(xs), max(xs)]
            else: atual[1] = y; atual[2] = min(atual[2], min(xs)); atual[3] = max(atual[3], max(xs))
        elif atual is not None:
            out.append(atual); atual = None
    if atual: out.append(atual)
    for a in out:
        print(f"y {a[0]-y0:4d}-{a[1]-y0:4d} (h{a[1]-a[0]+1:3d})  x {a[2]-x0:4d}-{a[3]-x0:4d} (w{a[3]-a[2]+1:4d})  centro {((a[2]+a[3])/2 - x0) - (x1-x0)/2:+.1f}")
    print("fundo", fundo)
faixas(sys.argv[1], tuple(map(int, sys.argv[2:6])))
