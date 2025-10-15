from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QButtonGroup


class SelectBtns(QWidget):

    def __init__(self, change_image):
        super().__init__()

        layout = QHBoxLayout(self)
        self.change_image = change_image

        # 버튼 생성
        self.btn1 = QPushButton("전체 답안")
        self.btn1.setProperty("type", "main")

        self.btn2 = QPushButton("백지 답안")
        self.btn2.setProperty("type", "blank")

        self.btn3 = QPushButton("중복 답안")
        self.btn3.setProperty("type", "double")

        self.remove_border()
        self.btn1.setStyleSheet("border-bottom: 1px solid white")

        # 버튼 그룹 생성 (exclusive=True로 단일 선택)
        self.group = QButtonGroup()
        self.group.setExclusive(True)  # 단일 선택 가능
        self.group.addButton(self.btn1)
        self.group.addButton(self.btn2)
        self.group.addButton(self.btn3)

        # 클릭 시 상태 확인
        self.group.buttonClicked.connect(self.on_button_clicked)

        layout.addWidget(self.btn1)
        layout.addWidget(self.btn2)
        layout.addWidget(self.btn3)

        self.setLayout(layout)

    def remove_border(self):
        self.btn1.setStyleSheet("border: none; padding: 0px 5px;")
        self.btn2.setStyleSheet("border: none; padding: 0px 5px;")
        self.btn3.setStyleSheet("border: none; padding: 0px 5px;")

    def on_button_clicked(self, button):
        self.remove_border()

        button.setStyleSheet("border-bottom: 1px solid white")

        btn_type = button.property("type")
        self.change_image(btn_type)
