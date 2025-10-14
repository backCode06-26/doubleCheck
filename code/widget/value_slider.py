from PySide6.QtWidgets import QWidget, QSlider, QLabel, QVBoxLayout
from PySide6.QtCore import Qt


class ValueSlider(QWidget):
    def __init__(self):
        super().__init__()

        # 슬라이딩 방식의 입력폼
        main_left_slider = QSlider(Qt.Horizontal)
        main_left_slider.setValue(5)
        main_left_slider.setMinimum(0)
        main_left_slider.setMaximum(10)
        main_left_slider.setSingleStep(1)

        main_left_slider.valueChanged.connect(self.on_value_change)

        # 현재 입력 폼의 표시값
        self.main_left_slider_label = QLabel("현재 Hash값: 5")
        self.main_left_slider_label.setProperty("hash_value", 5)

        layout = QVBoxLayout()
        layout.addWidget(main_left_slider)
        layout.addWidget(self.main_left_slider_label)

        self.setLayout(layout)

    def on_value_change(self, value):
        self.main_left_slider_label.setText(f"현재 Hash값: {value}")
        self.main_left_slider_label.setProperty("hash_value", value)

    def get_hash_value(self):
        return self.main_left_slider_label.property("hash_value")
