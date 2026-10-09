import sys, types, threading
sys.path.insert(0, "/home/user/sig-ft")
m = types.ModuleType("sigft.app.widgets.dialogs"); m.MSG_EXCEL_BLOQUEADO="x"; m.TEXTO_CONTINUAR="c"; m.msg_excel_bloqueado=lambda c: "x"
sys.modules["sigft.app.widgets.dialogs"] = m
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt
app = QApplication([])
from sigft.app_qt.widgets import dialogs as qd
for cls, kw in ((qd.PausaLoginDialog, dict(mensagem="x")), (qd.RetryLockDialog, dict(resultado={}))):
    ev = threading.Event()
    w = QWidget()
    d = cls(w, evento_espera=ev, **kw)
    d.show()
    QTest.keyClick(d, Qt.Key.Key_Escape)
    print(cls.__name__, "Esc -> event set:", ev.is_set(), "visible:", d.isVisible())
