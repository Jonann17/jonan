"""Medidas de tinta em capturas. Uso: medir.py img x0 y0 x1 y1 [cor_hex tol | lum limiar]"""
import sys
from PIL import Image

def extensao(img, caixa, pred):
    im = Image.open(img).convert("RGB")
    x0, y0, x1, y1 = caixa
    xs, ys = [], []
    for y in range(y0, y1):
        for x in range(x0, x1):
            if pred(im.getpixel((x, y))):
                xs.append(x); ys.append(y)
    if not xs:
        return None
    return min(xs), max(xs), max(xs) - min(xs) + 1, min(ys), max(ys)

def perto(cor, tol):
    r, g, b = int(cor[1:3], 16), int(cor[3:5], 16), int(cor[5:7], 16)
    return lambda p: abs(p[0]-r) + abs(p[1]-g) + abs(p[2]-b) <= tol

def claro(lim):
    return lambda p: sum(p) / 3 >= lim

if __name__ == "__main__":
    img = sys.argv[1]; caixa = tuple(map(int, sys.argv[2:6]))
    modo, arg = sys.argv[6], sys.argv[7]
    pred = perto(arg, int(sys.argv[8])) if modo == "cor" else claro(float(arg))
    print(extensao(img, caixa, pred))
