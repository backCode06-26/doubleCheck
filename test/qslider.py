import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QSlider
from PySide6.QtCore import Qt

class SliderExample(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QSlider Example")
        self.resize(300, 150)

        self.layout = QVBoxLayout()
        self.label = QLabel("현재 값: 0")
        self.slider = QSlider(Qt.Horizontal)

        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setSingleStep(1)
        self.slider.valueChanged.connect(self.on_value_change)

        self.layout.addWidget(self.slider)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

    def on_value_change(self, value):
        float_value = value / 10  # 다시 0.1 단위로 변환
        self.label.setText(f"현재 값: {float_value:.1f}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SliderExample()
    window.show()
    sys.exit(app.exec())
