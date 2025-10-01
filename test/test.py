from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout


class ToggleWidgetDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hide/Show Widget Example")

        layout = QVBoxLayout(self)

        # 숨기거나 보일 위젯
        self.target_widget = QPushButton("I am a target widget")
        layout.addWidget(self.target_widget)

        # 토글 버튼
        self.toggle_button = QPushButton("Hide / Show")
        self.toggle_button.clicked.connect(self.toggle_widget)
        layout.addWidget(self.toggle_button)

    def toggle_widget(self):
        # 위젯 숨기거나 보이게 하기
        if self.target_widget.isVisible():
            self.target_widget.hide()
        else:
            self.target_widget.show()


if __name__ == "__main__":
    app = QApplication([])

    demo = ToggleWidgetDemo()
    demo.show()

    app.exec()
