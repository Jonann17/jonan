"""Captura a tela Qt ModuloLMR avulsa (registrada em TELAS só aqui) e os dois diálogos."""
import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from sigft.app import backends
from sigft.app_qt import main as qmain
from sigft.app_qt.views.lmr import DialogoDaAba, ModuloLMR
from sigft.app_qt.widgets.dialogs import SelecaoComCaixasDialog

saida = sys.argv[1]
qmain.TELAS["LMRAvulsa"] = lambda p, c: ModuloLMR(p, c)
qmain._preparar_qt()
backends.carregar_todos()
janela = qmain.SIG_FT_App()
janela.resize(1280, 850)
janela.show()
janela.show_frame("LMRAvulsa")
def esperar():
    for _ in range(30):
        QApplication.processEvents()
esperar()
janela.grab().save(f"{saida}/qt_lmr.png")
t = janela.telas["LMRAvulsa"]
def g(w, n, d=0, base=janela):
    p = w.mapTo(base, w.rect().topLeft())
    print("  " * d + n, "x", p.x(), "y", p.y(), "w", w.width(), "h", w.height())
g(t, "tela"); g(t.header, "header"); g(t.label_titulo, "titulo"); g(t.content, "content"); g(t.console, "console")
card = t.btn_run.parentWidget(); g(card, "card")
for nome, w in t._rotulos.items():
    g(w, nome, 1)
g(t.picker_status, "picker", 1); g(t.picker_status.botao, "picker.botao", 2); g(t.picker_status.label_status, "picker.label", 2)
g(t.btn_run, "btn_run", 1); g(t.caixa_linha_inicial, "interruptor", 1); g(t.entry_linha_inicial, "entry", 1)
t.caixa_linha_inicial.setChecked(True)
t.entry_linha_inicial.setText("12")
esperar()
janela.grab().save(f"{saida}/qt_lmr_ligado.png")

d = DialogoDaAba(janela, nome_arquivo="LMR_Aplicacoes_2026.xlsx", abas=["Plan1", "LMR", "GERAL"])
d.show(); esperar()
d.grab().save(f"{saida}/qt_dialogo_aba.png")
print("== dialogo aba", d.width(), d.height())
for n in ("rotulo_arquivo", "rotulo_pergunta", "menu", "botao_ler", "botao_cancelar"):
    g(getattr(d, n), n, 1, d)
d.close()

s = SelecaoComCaixasDialog(janela, titulo="Selecione as Fichas", mensagem="Selecione os PMIBs para processar:",
                           itens=[f"4500063671.{i:04d}" for i in range(1, 31)])
s.lista.item(1).setCheckState(Qt.CheckState.Checked); s.lista.item(3).setCheckState(Qt.CheckState.Checked)
s.show(); esperar()
s.grab().save(f"{saida}/qt_dialogo_pmibs.png")
print("== dialogo pmibs", s.width(), s.height())
for n in ("rotulo", "quadro", "lista", "botao_todos", "botao_confirmar"):
    g(getattr(s, n), n, 1, s)
r = s.lista.visualItemRect(s.lista.item(0)); p = s.lista.viewport().mapTo(s, r.topLeft())
print("  item0", p.x(), p.y(), r.width(), r.height())
sb = s.lista.verticalScrollBar(); g(sb, "scrollbar", 1, s)
s.close()
