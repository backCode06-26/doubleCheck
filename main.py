from PySide6.QtWidgets import QApplication
from code.widget.omr_gui import omr_gui
import sys


def main():
    app = QApplication(sys.argv)
    window = omr_gui()
    window.showMaximized()
    app.exec()


if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support()
    main()
