import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt
app=QApplication([])
from sigft.app_qt.views import analyzer as a
from types import SimpleNamespace
t=a.ModuloAnalyzer(None,None)
saved=[]
t._salvar_pesos=lambda w: saved.append(1)
w=a.JanelaPesos(t,{"x":{"weight":1}}); w.show()
print("default", w.btn_salvar.isDefault(), w.btn_salvar.autoDefault())
t.entries_pesos["x"].setFocus()
QTest.keyClick(t.entries_pesos["x"],Qt.Key_Return)
print("enter saved:",saved)
t.entries_pesos["x"].setText("9")
QTest.keyClick(w,Qt.Key_Escape)
print("esc visible:",w.isVisible())
