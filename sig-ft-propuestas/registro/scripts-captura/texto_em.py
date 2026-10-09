import sys
from PIL import Image
arq, x0, y0, x1, y1, cor = sys.argv[1], *map(int, sys.argv[2:6]), sys.argv[6]
alvo = tuple(int(cor[i:i+2], 16) for i in (1, 3, 5))
im = Image.open(arq).convert("RGB")
pts = [(x, y) for x in range(x0, x1) for y in range(y0, y1)
       if sum(abs(a - b) for a, b in zip(im.getpixel((x, y)), alvo)) < 120]
xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
print(f"x {min(xs)-x0}-{max(xs)-x0} (w{max(xs)-min(xs)+1}) y {min(ys)-y0}-{max(ys)-y0} (h{max(ys)-min(ys)+1})")
