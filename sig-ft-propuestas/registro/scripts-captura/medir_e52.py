"""Compara capturas CTk x Qt da JanelaAtualizacao: caixas de tinta por regiao."""
import sys

from PIL import Image, ImageChops

pasta, estado = sys.argv[1], sys.argv[2]
a = Image.open(f"{pasta}/ctk_{estado}.png").convert("RGB")
b = Image.open(f"{pasta}/qt_{estado}.png").convert("RGB")
print("tamanhos", a.size, b.size)


def tinta(img, caixa, fundo, limiar=40):
    """bbox (relativo a img) dos pixels que diferem do fundo na regiao."""
    reg = img.crop(caixa)
    dif = ImageChops.difference(reg, Image.new("RGB", reg.size, fundo)).convert("L")
    dif = dif.point(lambda v: 255 if v > limiar else 0)
    bb = dif.getbbox()
    if not bb:
        return None
    return (bb[0] + caixa[0], bb[1] + caixa[1], bb[2] + caixa[0], bb[3] + caixa[1])


def linhas(img, caixa, fundo, limiar=60):
    """faixas verticais (y0, y1) com tinta: as linhas de texto."""
    reg = img.crop(caixa)
    dif = ImageChops.difference(reg, Image.new("RGB", reg.size, fundo)).convert("L")
    w, h = dif.size
    px = dif.load()
    faixas, dentro = [], None
    for y in range(h):
        tem = any(px[x, y] > limiar for x in range(w))
        if tem and dentro is None:
            dentro = y
        if not tem and dentro is not None:
            faixas.append((dentro + caixa[1], y + caixa[1]))
            dentro = None
    return faixas


FUNDO = (26, 26, 26)
NOTAS = (51, 51, 51)
regioes = {
    "titulo": ((0, 0, 580, 48), FUNDO),
    "resumo": ((0, 50, 580, 82), FUNDO),
    "o_que_mudou": ((0, 90, 580, 122), FUNDO),
    "notas_caixa": ((0, 124, 580, 452), FUNDO),
    "botao_atualizar_texto": ((125, 505, 285, 535), (3, 93, 103)),
    "botao_agora_nao_texto": ((315, 505, 455, 535), FUNDO),
    "status": ((0, 410, 580, 498), FUNDO),
}
for nome, (caixa, fundo) in regioes.items():
    print(f"{nome:24s} ctk={tinta(a, caixa, fundo)}  qt={tinta(b, caixa, fundo)}")
print("linhas notas ctk", linhas(a, (25, 130, 555, 300), NOTAS))
print("linhas notas qt ", linhas(b, (25, 130, 555, 300), NOTAS))
print("linhas status ctk", linhas(a, (20, 400, 560, 496), FUNDO))
print("linhas status qt ", linhas(b, (20, 400, 560, 496), FUNDO))
print("notas x ctk", tinta(a, (21, 130, 300, 300), NOTAS), "qt", tinta(b, (21, 130, 300, 300), NOTAS))
for p in [(300, 300), (200, 520), (380, 520), (311, 520), (5, 5)]:
    print("pixel", p, a.getpixel(p), b.getpixel(p))
