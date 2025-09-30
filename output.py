from PySide6.QtWidgets import (
    QVBoxLayout, QPlainTextEdit, QFrame
)
from PySide6.QtCore import Qt


class OutputOverlay(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 위젯의 독립창, 부모 위에 떠있게 하는 표시 스타일을 지정하는 플래그
        # Qt.SubWindow : 부모 위젯 안에 떠있는 보조 창의 스타일을 결정함

        self.setWindowFlags(Qt.SubWindow)

        self.setStyleSheet("""
            background-color: #1e1e1e;
            border: 2px solid #555555;
            color: #00ff00;
            font-family: 'Courier New', monospace;
            font-size: 12pt;
        """)

        self.resize(1000, 400)

        layout = QVBoxLayout(self)

        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

    def write(self, text):
        self.output.appendPlainText(text)

    def flush(self):
        pass
