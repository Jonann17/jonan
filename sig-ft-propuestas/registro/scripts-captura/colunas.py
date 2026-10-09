import sys
from PIL import Image
arq, x0, y0, y1, xa, xb = sys.argv[1], *map(int, sys.argv[2:7])
im = Image.open(arq).convert("RGB")
fundo = (43, 43, 43)
cols = [x for x in range(xa, xb) if any(sum(abs(a-b) for a, b in zip(im.getpixel((x, y)), fundo)) > 40 for y in range(y0, y1))]
seg = []
for x in cols:
    if seg and x - seg[-1][1] <= 6: seg[-1][1] = x
    else: seg.append([x, x])
print([(a - x0, b - x0, b - a + 1) for a, b in seg])
