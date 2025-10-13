import os
import sys
from PySide6.QtWidgets import QApplication, QLabel
from PySide6.QtCore import Qt

class DoubleClickLabel(QLabel):
    def __init__(self, text):
        super().__init__(text)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("background-color: lightgray; font-size: 20px;")
        self.setFixedSize(300, 100)

    def mouseDoubleClickEvent(self, event):
        # 마우스 왼쪽 버튼 더블 클릭 시
        if event.button() == Qt.LeftButton:
            image_path = r"C:\Users\유호진\Desktop\doubleCheck\system\null_image.JPG"
            os.startfile(image_path)
            
            self.setText("더블 클릭됨!")
            self.setStyleSheet("background-color: lightgreen; font-size: 20px;")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    label = DoubleClickLabel("라벨을 더블 클릭하세요")
    label.show()
    sys.exit(app.exec())
