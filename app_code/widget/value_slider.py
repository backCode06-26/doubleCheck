import config

from PySide6.QtWidgets import QWidget, QSlider, QLabel, QVBoxLayout
from PySide6.QtCore import Qt


class ValueSlider(QWidget):
    def __init__(self, value, min, max, value_name):
        super().__init__()

        layout = QVBoxLayout(self)
        self.value_name = value_name

        # 슬라이딩 방식의 입력폼
        slider = QSlider(Qt.Horizontal)
        slider.setValue(value)
        slider.setMinimum(min)
        slider.setMaximum(max)
        slider.setSingleStep(1)

        slider.valueChanged.connect(self.onValueChange)

        # 현재 입력 폼의 표시값
        self.slider_label = QLabel(f"현재 값: {value}")

        layout.addWidget(slider)
        layout.addWidget(self.slider_label)

    # 현재 값을 업데이트 하는 함수
    def onValueChange(self, value):
        self.slider_label.setText(f"현재 값: {value}")

        if self.value_name == "hash":
            config.hash_value = value
        elif self.value_name == "cpu":
            config.core_count = value

