from pathlib import Path

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

        self.label = QLabel("답안: ")
        self.dropdown = QComboBox()

        # 레이아웃 위젯 추가
        layout.addWidget(self.label)
        layout.addWidget(self.dropdown)

        # 계열 드롭다운이 변경될 때 작동
        self.dropdown.currentTextChanged.connect(self.load_image)


    def update_item(self, json_paths):

        for json_path in json_paths:
            json_name = Path(json_path).stem
            self.dropdown.addItem(json_name, json_path)

    # 멀티 쓰레드를 할때 이거가 먼저 작동되는 문제가 있어서 해결해야함
    def load_image(self):
        json_path = self.dropdown.currentData()

        config.current_json = json_path

        try:
            self.update_image("main")
        except Exception as e:
            print("update_image error:", e)
