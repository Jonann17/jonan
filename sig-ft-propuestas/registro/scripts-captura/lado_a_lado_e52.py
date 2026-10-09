import sys

from PIL import Image

pasta = sys.argv[1]
for estado in sys.argv[2:]:
    a = Image.open(f"{pasta}/ctk_{estado}.png")
    b = Image.open(f"{pasta}/qt_{estado}.png")
    lado = Image.new("RGB", (a.width + b.width + 10, max(a.height, b.height)), (255, 0, 255))
    lado.paste(a, (0, 0))
    lado.paste(b, (a.width + 10, 0))
    lado.save(f"{pasta}/lado_a_lado_{estado}.png")
