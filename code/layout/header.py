import os
from pathlib import Path
import config

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog
)

from code.widget.select_btns import SelectBtns
from code.widget.zoom_slider import ZoomSlider
from code.widget.image_dropdown import Dropdown

from PySide6.QtCore import QThreadPool
from code._threads.image_preprocessing import ImagePreprocessingRunnable

from code.core.data_processor import dataProcessing, saveJson
from code.process.image_processor import ImageProcessor


class Header(QWidget):
    def __init__(
        self,
        updateImage,
        updateScaleView,
        toggleSubmitButton
    ):
        super().__init__()

        # 변수
        self.existing_path = ""  # 현재 폴더경로 (문자열로 유지)

        # 함수
        self.updateImage = updateImage
        self.updateScaleView = updateScaleView
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

        self.update_image_button = SelectBtns(
            self.updateImage)  # 전체, 백지, 중복 이미지를 선택하는 위젯
        self.update_image_dropdown = Dropdown()  # 교시, 교사실 번호를 선택하는 위젯
        self.scale_slider = ZoomSlider(
            self.updateScaleView)  # 이미지의 크기를 조절하는 위젯

        # nav_layout 위젯 추가
        nav_layout.addWidget(self.update_image_button, 6)
        nav_layout.addWidget(self.update_image_dropdown)
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
        # QFileDialog는 경로를 문자열로 반환합니다.
        new_folder_path_str = QFileDialog.getExistingDirectory(
            self, "이미지 폴더를 선택해주세요")

        if new_folder_path_str:
            new_folder_path = Path(new_folder_path_str)

            # 현재 경로와 다른지 비교
            if self.existing_path != new_folder_path_str:

                # 현재 경로로 지정
                self.existing_path = new_folder_path_str

                depth_data = {}
                max_depth_observed = 0  # 최대 깊이 추적용

                # 지정한 파일의
                for root_str, dirs, files in os.walk(self.existing_path):

                    # 현재 경로 추출
                    current_path = Path(root_str)

                    try:
                        # / 기준으로 경로를 배열로 변경합니다.
                        parts_list = list(Path(root_str).parts)
                        # 배열로 만든 경로를 기준으로 마지막 3개의 경로만 가져옵니다.
                        major_code, class_period, classroom_code = parts_list[-3:]

                        parts_tuple = (
                            major_code, class_period, classroom_code)
                    except ValueError:
                        if current_path == new_folder_path:
                            parts_tuple = ()
                        else:
                            continue

                    # '.', 'data'를 제외한 경로만 가져옵니다.
                    cleaned_parts = [
                        part for part in parts_tuple
                        if part and part != '.' and part != 'data'
                    ]

                    current_depth = len(cleaned_parts)
                    max_depth_observed = max(max_depth_observed, current_depth)

                    # 현재 깊이를 키로 사용하여 데이터 저장
                    if current_depth not in depth_data:
                        depth_data[current_depth] = []

                    # depth_data에 저장 (root: 경로, parts: 계열, 교시, 고사실 번호)
                    depth_data[current_depth].append({
                        "root": root_str,
                        "parts": parts_tuple
                    })

                # 데이터 필터링
                final_processing_list = depth_data.get(max_depth_observed, [])

                for item in final_processing_list:
                    current_root = item["root"]

                    major_code, class_period, classroom_code = item["parts"]

                    json_name = f"{major_code}{class_period}{classroom_code}.json"

                    dataProcessing(current_root, json_name)

                # 전체 경로 저장
                config.OUTPUT_FOLDER_PATH = self.existing_path

                print("이미지 경로 저장 및 불러오기를 완료했습니다.\n")
                # self.toggleButton()
            else:
                print("선택하신 폴더가 이전의 폴더의 경로와 같습니다.\n")
                # self.toggleButton()
        else:
            print("이미지 폴더 선택을 취소하셨습니다.\n")
