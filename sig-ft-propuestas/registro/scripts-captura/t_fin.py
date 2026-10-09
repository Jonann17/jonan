from PySide6.QtWidgets import QApplication, QWidget, QDialog
app = QApplication([])
p = QWidget(); p.show()
d = QDialog(p); fired=[]
d.finished.connect(lambda r: fired.append(('fin',r)))
d.show()
d.hide(); print("after hide", fired)
d.show()
p.deleteLater(); app.processEvents(); 
import PySide6; print(PySide6.__version__, "after parent delete", fired)
