import os

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog
)

from code.widget.select_btns import SelectBtns
from code.widget.zoom_slider import ZoomSlider

from PySide6.QtCore import QThreadPool
from code._threads.image_preprocessing import ImagePreprocessingRunnable

from code.core.data_processor import dataProcessing, saveJson


class Header(QWidget):
    def __init__(
        self,
        updateImage,
        updateScaleView,
        toggleSubmitButton
    ):
        super().__init__()

        # 변수
        self.existing_path = ""  # 현재 폴더경로

        # 함수
        self.updateImage = updateImage  # 이미지 로드 함수
        self.updateScaleView = updateScaleView  # 이미지 확대 축소 함수
        self.toggleSubmitButton = toggleSubmitButton

        # header_layout 추가
        header_layout = QVBoxLayout(self)

        # 폴더 경로를 선택하는 GUI
        self.update_folder_button = QPushButton("폴더를 선택해주세요")
        self.update_folder_button.setStyleSheet(
            "padding: 5px 8px; font-size: 16px;")
        self.update_folder_button.clicked.connect(self.updatePath)

        # nav_layout 추가
        nav_layout = QHBoxLayout()

        # 전체, 중복, 백지 답안을 보여주는 토글 버튼
        self.update_image_button = SelectBtns(self.updateImage)
        self.scale_slider = ZoomSlider(self.updateScaleView)

        # nav_layout 위젯 추가
        nav_layout.addWidget(self.update_image_button, 6)
        nav_layout.addStretch(15)
        nav_layout.addWidget(self.scale_slider, 1)

        # header_layout 위젯 추가
        header_layout.addWidget(self.update_folder_button)
        header_layout.addLayout(nav_layout)

    def toggleButton(self):
        enable = not self.update_folder_button.isEnabled()
        self.toggleSubmitButton(enable)
        self.update_folder_button.setEnabled(enable)

    def toFinish(self):
        print("작업을 완료하였습니다.")
        self.toggleButton()

    def runImagePrecess(self, image_paths):
        self._thread = QThreadPool()

        self.runnable = ImagePreprocessingRunnable(image_paths)
        self.runnable.signals.progress.connect(print)
        self.runnable.signals.error.connect(print)
        self.runnable.signals.result.connect(
            lambda results: saveJson(results, "data"))
        self.runnable.signals.finished.connect(self.toFinish)

        self._thread.start(self.runnable)

    def updatePath(self):

        # 새로 받을 폴터 경로
        print("이미지 폴터를 선택하고 있습니다.")
        self.new_folder_path = QFileDialog.getExistingDirectory(
            self, "이미지 폴더를 선택해주세요")

        if self.new_folder_path:
            # 현재 경로와 다른 경로만 저장
            if self.existing_path != self.new_folder_path:

                # 현재 경로로 지정
                self.existing_path = self.new_folder_path

                self.toggleButton()

                print("폴더 안 이미지의 경로 가져오는 중입니다.")
                IMAGE_EXTENSIONS = (
                    ".png", ".jpg", ".jpeg", ".bmp")  # 허용되는 확장자

                # 확장자 검사
                self.image_paths = [
                    os.path.join(self.existing_path, f).replace("\\", "/")
                    for f in os.listdir(self.existing_path)
                    if f.lower().endswith(IMAGE_EXTENSIONS)
                ]

                self.back_image_paths = [
                    f
                    for f in self.image_paths
                    if os.path.splitext(os.path.basename(f))[0][-1] == "2"
                ]

                # 이미지가 존재하는지 확인합니다.
                if not self.image_paths:
                    print("선택한 폴더에 이미지가 없습니다.")
                    self.toggleButton()
                    return

                # 시작전 기본 설정
                dataProcessing(self.existing_path)

                # 저장된 위치
                mode = "main"
                saveJson(self.image_paths, mode)  # 이미지 저장

                self.runImagePrecess(self.back_image_paths)

                self.updateImage(mode)  # 이미지 변경

                print("이미지 경로 저장 및 불러오기를 완료했습니다.\n")
            else:
                print("선택하지 폴더가 이전의 폴더의 경로와 같습니다.\n")
                self.toggleButton()
        else:
            print("이미지 폴더 선택을 취소하셨습니다.\n")
