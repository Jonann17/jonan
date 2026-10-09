from PySide6.QtCore import Qt, QPoint
from PySide6.QtWidgets import QLabel
from sigft.app_qt.views.home import HomeView

class C:
    def __init__(s): s.v=[]
    def show_frame(s,n): s.v.append(n)

def test_x(qt_interface, qtbot):
    c=C(); h=HomeView(controller=c); qtbot.addWidget(h); h.resize(1000,800); h.show()
    card=h.cards["Analyzer"]
    for nome in ("card_titulo","card_desc"):
        lab=card.findChild(QLabel,nome)
        qtbot.mouseClick(lab, Qt.MouseButton.LeftButton, pos=lab.rect().center())
    print(c.v)
    # real hit-test via window coordinates
    c.v.clear()
    lab=card.findChild(QLabel,"card_desc")
    gp=lab.mapTo(h.viewport(), lab.rect().center())
    qtbot.mouseClick(h.viewport(), Qt.MouseButton.LeftButton, pos=gp)
    print("viewport", c.v)
    assert c.v==["Analyzer"]
