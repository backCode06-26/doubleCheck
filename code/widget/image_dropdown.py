from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QComboBox, QLabel
)


class Dropdown(QWidget):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout(self)

        self.academic_field_label = QLabel("계열: ")
        self.academic_field_dropdown = QComboBox()  # 교시 드롭다운
        self.academic_field_dropdown.addItem("계열 없음", None)  # 기본값

        self.period_label = QLabel("교시: ")
        self.period_dropdown = QComboBox()  # 교시 드롭다운
        self.period_dropdown.addItem("교시 없음", None)  # 기본값

        self.exam_room_label = QLabel("고사실 번호: ")
        self.exam_room_dropdown = QComboBox()  # 교사실 드롭다운
        self.exam_room_dropdown.addItem("고사실 번호 없음", None)

        layout.addWidget(self.academic_field_label)
        layout.addWidget(self.academic_field_dropdown)
        layout.addStretch(2)
        layout.addWidget(self.period_label)
        layout.addWidget(self.period_dropdown)
        layout.addStretch(2)
        layout.addWidget(self.exam_room_label)
        layout.addWidget(self.exam_room_dropdown)

    def addDropDonwData(self, datas, type="pd"):
        """
        계열(af) 또는 교시(pd), 고사실 번호(er) 드롭다운을 추가합니다.
        type 매개변수에는 'pd' 또는 'er'을 지정하세요.
        """
        target = self.academic_field_dropdown if type == "af" else (
            self.period_dropdown if type == "pd" else self.exam_room_dropdown)
        value_name = "계열" if type == "af" else (
            "교시" if type == "pd" else "고사실 번호")

        target.clear()

        for value in datas:
            target.addItem(f"{value_name} {value}", value)
