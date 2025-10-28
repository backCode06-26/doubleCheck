from PySide6.QtWidgets import QApplication
from code.widget.omr_gui import omr_gui
import sys

app = QApplication(sys.argv)

window = omr_gui()

window.showMaximized()
app.exec()
