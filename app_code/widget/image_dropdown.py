from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QComboBox, QLabel
)

import config
from app_code.core.data_processor import read_json


class ImageDropDown(QWidget):
    def __init__(self, update_image):
        super().__init__()

        self.data = None
        self.update_image = update_image

        layout = QHBoxLayout(self)

        self.label = QLabel("계열: ")
        self.dropdown = QComboBox()

        # 레이아웃 위젯 추가
        layout.addWidget(self.label)
        layout.addWidget(self.dropdown)

        # 계열 드롭다운이 변경될 때 작동
        self.dropdown.currentIndexChanged.connect(self.load_image)

    def update_item(self, json_paths):
        self.dropdown.addItems(json_paths)

    def load_image(self):
        json_path = self.dropdown.currentText()
        print(json_path)

        config.current_json = json_path

        self.update_image("main")
