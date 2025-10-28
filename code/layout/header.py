import os

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog
)
from PySide6.QtCore import QThreadPool

from code.widget.select_btns import SelectBtns
from code.widget.zoom_slider import ZoomSlider

from code._threads.image_preprocessing import run_processing

from code.core.data_processor import data_processing, saveJson

class Header(QWidget):
    def __init__(
            self, 
            updateImage,
            updateScaleView         
        ):
        super().__init__()

        # 변수
        self.existing_path = "" # 현재 폴더경로

        # 함수
        self.updateImage = updateImage # 이미지 로드 함수
        self.updateScaleView = updateScaleView # 이미지 확대 축소 함수

        # header_layout 추가
        header_layout = QVBoxLayout(self)

        # 폴더 경로를 선택하는 GUI
        update_folder_button = QPushButton("폴더를 선택해주세요")
        update_folder_button.setStyleSheet("padding: 5px 8px; font-size: 16px;")
        update_folder_button.clicked.connect(self.updatePath)

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
        header_layout.addWidget(update_folder_button)
        header_layout.addLayout(nav_layout)

    # 폴더의 경로와 폴더 안의 이미지의 경로을 지정하는 함수
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

                print("폴더 안 이미지의 경로 가져오는 중입니다.")
                IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".bmp") # 허용되는 확장자

                def isBlack(path):
                    file_name = os.path.basename(path)
                    file_name = os.path.splitext(file_name)[0]
                    return True if file_name[-1] == "2" else False

                # 확장자 검사
                self.image_paths = [
                    os.path.join(self.existing_path, f).replace("\\", "/")
                    for f in os.listdir(self.existing_path)
                    if isBlack(f)
                    if f.lower().endswith(IMAGE_EXTENSIONS)
                ]

                # 이미지가 존재하는지 확인합니다.
                if not self.image_paths:
                    print("선택한 폴더에 이미지가 없습니다.")
                    return
                
                # 시작전 기본 설정
                data_processing(self.existing_path)

                # 이미지 전처리
                run_processing(self.image_paths)

                # 저장된 위치
                mode = "main"
                saveJson(self.image_paths, mode) # 이미지 저장
                self.updateImage(mode) # 이미지 변경

                print("이미지 경로 저장 및 불러오기를 완료했습니다.\n")
            else:
                print("선택하지 폴더가 이전의 폴더의 경로와 같습니다.\n")
        else:
            print("이미지 폴더 선택을 취소하셨습니다.\n")



