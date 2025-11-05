from PySide6.QtWidgets import QWidget, QVBoxLayout, QSlider, QLabel
from PySide6.QtCore import Qt


class ZoomSlider(QWidget):
    def __init__(self, zoom_img):
        super().__init__()

        self.zoom_img = zoom_img

        layout = QVBoxLayout(self)

        slider = QSlider(Qt.Horizontal)
        slider.setValue(10)
        slider.setMinimum(5)
        slider.setMaximum(15)
        slider.setSingleStep(1)

        self.label = QLabel(f"현재 배율: {100}%")

        slider.valueChanged.connect(self.scale_controll)

        layout.addWidget(slider)
        layout.addWidget(self.label)

    def scale_controll(self, value):
        persent = value * 10
        self.label.setText(f"현재 배율: {persent}%")

        try:
            factor = value / 10
            self.zoom_img(factor)
        except Exception as e:
            print(f"아직 이미지가 없습니다. {e}")
