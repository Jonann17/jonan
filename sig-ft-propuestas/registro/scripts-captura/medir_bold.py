import sys
sys.path.insert(0, "/tmp/claude-0/-home-user/111ccf73-6723-5e3b-a4c3-03916583ae47/scratchpad")
from medir import extensao
vermelho = lambda p: p[0] - p[1] > 80
branco = lambda p: min(p) > 150
CX = {"titulo": (290, 25, 700, 65, vermelho), "atencao": (330, 118, 1230, 146, vermelho),
      "pmib_rot": (560, 214, 700, 242, branco), "iniciar": (610, 370, 950, 402, branco)}
for img in sys.argv[1:]:
    print(img.split("paridade-global/")[-1])
    for k, v in CX.items():
        e = extensao(img, v[:4], v[4])
        print(f"   {k:10s} x={e[0]}..{e[1]} largura={e[2]}  y={e[3]}..{e[4]}")
