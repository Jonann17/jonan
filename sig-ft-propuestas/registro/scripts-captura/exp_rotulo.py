import sys
from PySide6.QtGui import QFont, QFontMetricsF
from PySide6.QtWidgets import QApplication, QLabel
from sigft.app_qt import estilo
app = QApplication([])
estilo.carregar_fontes()
if sys.argv[1] == "padrao":
    f = QApplication.font(); f.setHintingPreference(QFont.HintingPreference.PreferDefaultHinting); QApplication.setFont(f)
app.setStyleSheet(estilo.folha_de_estilo())
T = {"passos12": ("O robô irá:\n1. Abrir o navegador\n2. Solicitar login manual\n3. Acessar a ficha\n4. Clicar em todas as lixeiras até esvaziar a lista.", 12),
     "irrev13": ("Esta ferramenta apaga TODAS as aplicações LMR de uma ficha.\nO processo é irreversível.", 13),
     "opc12": ("Opcional: informe o _STATUS_PMIB para LIMPAR a marcação da coluna\n\"APLICAÇÃO - LMR\" das fichas que forem apagadas com sucesso.", 12)}
for k, (t, px) in T.items():
    l = QLabel(t); l.setStyleSheet(f"font-size: {px}px;"); l.ensurePolished()
    fm = QFontMetricsF(l.font())
    print(sys.argv[1], k, "sizeHint", l.sizeHint().height(), "lineSpacing", round(fm.lineSpacing(), 2), "height", round(fm.height(), 2), "ascent", round(fm.ascent(),2), "descent", round(fm.descent(),2), "hint", l.font().hintingPreference())
