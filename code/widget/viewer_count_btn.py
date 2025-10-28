import os

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout,
    QLabel, QPushButton
)


class ViewerCountBtn(QWidget):
    def __init__(self, parent, mode="main"):
        super().__init__(parent)

        mode_map = {
            "main": ("전체", ""),
            "blank": ("백지", "blank"),
            "double": ("중복", "double")
        }

        label, self.folder_name = mode_map.get(mode, ("알 수 없음", ""))
        self.parent = parent

        layout = QVBoxLayout(self)

        title_label = QLabel(f"{label} 답안 수")
        viewer_btn = QPushButton(f"{label} 답안 수")
        viewer_btn.clicked.connect(self.folderViewer)
        self.count_label = QLabel("0 장")

        layout.addWidget(title_label)
        layout.addWidget(viewer_btn)
        layout.addWidget(self.count_label)

    def folderViewer(self):
        try:
            folder_path = os.path.join(
                self.parent.existing_path, self.folder_name)
            os.startfile(folder_path)
        except Exception as e:
            print("지정된 경로는 존재하지 않습니다. 이미지 폴터를 선택해주세요")

    def setLabel(self, count):
        self.count_label.setText(f"{count} 장")
