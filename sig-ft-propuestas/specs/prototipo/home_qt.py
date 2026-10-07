"""Prototipo descartable: la Home del SIG-FT en PySide6, para comparar el aspecto.

No es parte de SIG-FT. Lee la paleta y los textos del propio proyecto para que la
comparación sea justa (mismos colores, mismos textos de los cards).
"""
import os
import sys

sys.path.insert(0, "/home/user/sig-ft")

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QFontDatabase, QPixmap
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QFrame, QGridLayout, QHBoxLayout, QLabel,
    QMainWindow, QPushButton, QScrollArea, QVBoxLayout, QWidget,
)

from sigft.app import theme

C = theme.COLORS
RAIZ = "/home/user/sig-ft"
EMOJI_MONO = "/tmp/claude-0/-home-user/111ccf73-6723-5e3b-a4c3-03916583ae47/scratchpad/fontes_baixadas/NotoEmoji-Regular.ttf"
FONTES = "/home/user/sig-ft/.venv/lib/python3.13/site-packages/customtkinter/assets/fonts/Roboto"

# Textos de los cards copiados de sigft/app/views/home.py (MODULOS), sin cambios.
import ast
_src = open(os.path.join(RAIZ, "sigft/app/views/home.py"), encoding="utf-8").read()
_arvore = ast.parse(_src)
MODULOS = next(
    ast.literal_eval(n.value) for n in _arvore.body
    if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "MODULOS"
)


def mono(texto: str) -> str:
    """Pide la version en blanco y negro de cada emoji (selector U+FE0E)."""
    return "".join(ch + "\ufe0e" if ord(ch) > 0x2000 and ch not in "\u2013\u2014" else ch
                   for ch in texto)


def cinza_tk(nn: int) -> str:
    v = round(255 * nn / 100)
    return f"#{v:02X}{v:02X}{v:02X}"


QSS = f"""
QMainWindow, #conteudo {{ background: {C['background']}; }}
#sidebar, #sidebar_interno {{ background: {C['sidebar']}; border: none; }}
QLabel {{ color: {C['text_light']}; font-family: Roboto; }}
#secao {{ color: {cinza_tk(50)}; font-size: 11px; font-weight: bold; padding-left: 10px; }}
#app_nome {{ color: {cinza_tk(60)}; font-size: 13px; }}
QPushButton {{ font-family: Roboto; border-radius: 6px; color: {C['text_light']}; }}
QPushButton[menu="true"] {{ background: transparent; text-align: left; padding: 0 10px;
                            min-height: 35px; max-height: 35px; font-size: 12px; border: none; }}
QPushButton[menu="true"]:hover {{ background: {C['primary']}; }}
QPushButton[menu="true"]:disabled {{ color: {cinza_tk(45)}; }}
#home {{ background: transparent; text-align: left; padding: 0 14px; min-height: 28px; font-size: 13px;
         font-weight: bold; border: 1px solid {cinza_tk(30)}; }}
#home:hover {{ background: {C['primary']}; }}
#titulo {{ font-size: 32px; font-weight: bold; color: {C['text_light']}; }}
#subtitulo {{ font-size: 16px; color: {cinza_tk(70)}; }}
#instrucao {{ font-size: 14px; color: {C['text_light']}; }}
QPushButton[barra="true"] {{ padding: 0 16px; min-height: 40px; font-size: 13px; font-weight: bold;
                             color: {C['text_white']}; border: none; }}
#card {{ background: {theme.COR_CARTAO}; border: 1px solid #333333; border-radius: 8px; }}
#card:hover {{ border: 1px solid {C['accent']}; }}
#card_titulo {{ color: {C['accent']}; font-size: 15px; font-weight: bold; }}
#card_desc {{ color: {cinza_tk(70)}; font-size: 12px; }}
QCheckBox {{ color: {C['text_light']}; font-family: Roboto; font-size: 12px; }}
QCheckBox::indicator {{ width: 20px; height: 20px; border: 2px solid {cinza_tk(45)};
                        border-radius: 6px; background: transparent; }}
QScrollBar:vertical {{ background: transparent; width: 10px; }}
QScrollBar::handle:vertical {{ background: #4A4D50; border-radius: 5px; min-height: 30px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; }}
"""

SIDEBAR = [
    ("secao", "INÍCIO DA FICHA"),
    ("btn", "1. Cria Fichas PMIB", False), ("btn", "2. Planilhas PMIB", False),
    ("btn", "3. Analyzer (IA)", False),
    ("secao", "DADOS TÉCNICOS & UPLOAD"),
    ("btn", "4.1. Upload Condições", False), ("btn", "4.2. Tradutor", False),
    ("btn", "4.3. Upload Specs", False), ("btn", "4.4. Correção de PDM", True),
    ("btn", "5. Upload duplicadas", False), ("btn", "6. AutoSpec AI (RAG)", False),
    ("btn", "7. Aplicação LMR", False),
    ("secao", "GESTÃO"),
    ("btn", "8. PMIB Manager", False), ("btn", "9. Search", False),
]


def montar_sidebar() -> QScrollArea:
    area = QScrollArea(objectName="sidebar")
    area.setFixedWidth(270)
    area.setWidgetResizable(True)
    area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    interno = QWidget(objectName="sidebar_interno")
    lay = QVBoxLayout(interno)
    lay.setContentsMargins(12, 26, 12, 12)
    lay.setSpacing(4)

    logo = QLabel()
    pix = QPixmap(os.path.join(RAIZ, "assets", "logo.png"))
    logo.setPixmap(pix.scaledToWidth(180, Qt.SmoothTransformation))
    logo.setAlignment(Qt.AlignCenter)
    lay.addWidget(logo)
    nome = QLabel("SIG-FT System", objectName="app_nome")
    nome.setAlignment(Qt.AlignCenter)
    lay.addWidget(nome)
    lay.addSpacing(22)
    lay.addWidget(QPushButton(mono("  🏠  Home"), objectName="home"))
    lay.addSpacing(6)
    for item in SIDEBAR:
        if item[0] == "secao":
            lay.addSpacing(20)
            lay.addWidget(QLabel(item[1], objectName="secao"))
            lay.addSpacing(5)
        else:
            b = QPushButton(item[1])
            b.setProperty("menu", True)
            b.setEnabled(not item[2])
            lay.addWidget(b)
    lay.addStretch()
    area.setWidget(interno)
    return area


def montar_home() -> QScrollArea:
    area = QScrollArea(objectName="conteudo")
    area.setWidgetResizable(True)
    area.setFrameShape(QFrame.NoFrame)
    w = QWidget(objectName="conteudo")
    lay = QVBoxLayout(w)
    lay.setContentsMargins(40, 30, 40, 30)
    lay.setSpacing(6)
    lay.addWidget(QLabel("SIG-FT", objectName="titulo"))
    lay.addWidget(QLabel("Sistema Integrado de Gestão de Fichas Técnicas - GE Vernova",
                         objectName="subtitulo"))
    lay.addSpacing(30)
    lay.addWidget(QLabel("Clique num módulo abaixo para abri-lo. Os botões desta barra abrem "
                         "painéis em janela, para a Home ficar limpa.", objectName="instrucao"))
    lay.addSpacing(6)

    barra = QHBoxLayout()
    barra.setSpacing(10)
    for texto, cor in [("📋  Atividades do dia", C["accent"]), ("🤖  Modelos de IA", C["primary"]),
                       ("💰  Gastos de IA", C["primary"]), ("🔑  Chaves de API", "#3A3A3A"),
                       ("🔄  Atualizações", "#3A3A3A")]:
        b = QPushButton(mono(texto))
        b.setProperty("barra", True)
        b.setStyleSheet(f"background: {cor};")
        barra.addWidget(b)
    barra.addWidget(QCheckBox("Versões de teste"))
    barra.addStretch()
    lay.addLayout(barra)
    lay.addSpacing(10)

    grade = QGridLayout()
    grade.setSpacing(12)
    for i, (_alvo, titulo, desc) in enumerate(MODULOS):
        card = QFrame(objectName="card")
        card.setCursor(Qt.PointingHandCursor)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(14, 12, 14, 12)
        cl.addWidget(QLabel(titulo, objectName="card_titulo"))
        d = QLabel(desc, objectName="card_desc")
        d.setWordWrap(True)
        cl.addWidget(d)
        grade.addWidget(card, i // 2, i % 2)
    lay.addLayout(grade)
    lay.addStretch()
    area.setWidget(w)
    return area


def main(saida: str):
    app = QApplication(sys.argv)
    for nome in ("Roboto-Regular.ttf", "Roboto-Medium.ttf"):
        QFontDatabase.addApplicationFont(os.path.join(FONTES, nome))
    # Iconos en blanco y negro: Noto Emoji (monocromatica, licencia OFL) va como
    # segunda familia, antes de que Qt busque la fuente de emoji a color del sistema.
    QFontDatabase.addApplicationFont(EMOJI_MONO)
    # Qt 6.9+: los emojis usan una fuente propia; se le indica la monocromatica.
    QFontDatabase.setApplicationEmojiFontFamilies(["Noto Emoji"])
    fonte = QFont()
    fonte.setFamilies(["Roboto", "Noto Emoji"])
    app.setFont(fonte)
    app.setStyleSheet(QSS.replace("font-family: Roboto;", 'font-family: "Roboto", "Noto Emoji";'))
    janela = QMainWindow()
    janela.setWindowTitle("SIG-FT - GE Vernova (prototipo Qt)")
    central = QWidget()
    h = QHBoxLayout(central)
    h.setContentsMargins(0, 0, 0, 0)
    h.setSpacing(0)
    h.addWidget(montar_sidebar())
    h.addWidget(montar_home(), 1)
    janela.setCentralWidget(central)
    janela.resize(1280, 850)
    janela.show()
    app.processEvents()
    janela.grab().save(saida)


if __name__ == "__main__":
    main(sys.argv[1])
