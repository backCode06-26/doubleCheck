from PySide6.QtWidgets import QApplication
from app_code.widget.main_window import MainWindow
import sys


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    app.exec()


if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support()
    main()
