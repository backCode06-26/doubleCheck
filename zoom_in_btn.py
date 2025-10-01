from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QButtonGroup


class ZoomInBtn(QWidget):
    def __init__(self, update_image_widht):
        super().__init__()

        layout = QHBoxLayout()

        # 확대 축소 기능 불완전 수정 필요
        plus_btn = QPushButton("+")
        # plus_btn.clicked.connect(lambda: update_image_widht("+"))
        plus_btn.resize(30, 30)
        plus_btn.setFixedSize(30, 30)

        minus_btn = QPushButton("-")
        # minus_btn.clicked.connect(lambda: update_image_widht("-"))
        minus_btn.resize(30, 30)
        minus_btn.setFixedSize(30, 30)

        layout.addWidget(plus_btn)
        layout.addWidget(minus_btn)

        self.setLayout(layout)
