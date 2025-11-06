from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel
)

from app_code.widget.value_slider import ValueSlider
import multiprocessing


class SubContainer(QWidget):
    def __init__(self):
        super().__init__()

        self.toggle = False
        cpu_count = multiprocessing.cpu_count() - 1

        self.setMaximumWidth(250)
        self.setMaximumWidth(150)

        # section 레이아웃
        self.section = QVBoxLayout()

        # 기준이 되는 Hash값을 받기 위한 입력폼
        self.hash_slider_lable = QLabel("이미지 유사도")
        self.hash_slider = ValueSlider(5, 0, 10, "hash")

        self.core_slider_lable = QLabel("사용될 코어의 개수")
        self.core_slider = ValueSlider(
            cpu_count, 1, cpu_count, "cpu")

        # section 위젯 추가
        self.section.addStretch(1)
        self.section.addWidget(self.hash_slider_lable)
        self.section.addWidget(self.hash_slider)
        self.section.addStretch(1)
        self.section.addWidget(self.core_slider_lable)
        self.section.addWidget(self.core_slider)
        self.section.addStretch(12)

        # sub_container 레이아웃 추가
        self.setLayout(self.section)

     # 레이아웃 토글 함수
    def toggle_layout(self):
        for i in range(self.section.count()):
            item = self.section.itemAt(i)
            widget = item.widget()
            if widget:
                if self.toggle == False:
                    widget.hide()

                elif self.toggle == True:
                    widget.show()

        self.toggle = True if not self.toggle else False
