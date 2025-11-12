import os
import time
import config
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QDialog
)

from app_code.widget.select_btns import SelectBtns
from app_code.widget.zoom_slider import ZoomSlider
from app_code.widget.image_dropdown import ImageDropDown

from PySide6.QtCore import QThreadPool
from app_code._threads.batch_image_precessor import BatchImagePreprocessingRunnable

from app_code.process.image_processor import ImageProcessor

from app_code.widget.image_crop import ImageCropPanel


class Header(QWidget):
    def __init__(
        self,
        update_image,
        update_scale_view,
        toggle_submit_button
    ):
        super().__init__()

        # 변수
        self.existing_path = ""  # 현재 폴더경로 (문자열로 유지)

        # 함수
        self.update_image = update_image
        self.update_scale_view = update_scale_view
        self.toggle_submit_button = toggle_submit_button

        # header_layout 추가
        header_layout = QVBoxLayout(self)

        # 폴더 경로를 선택하는 GUI
        self.update_folder_button = QPushButton("폴더를 선택해주세요")
        self.update_folder_button.setStyleSheet(
            "padding: 5px 8px; font-size: 16px;")
        self.update_folder_button.clicked.connect(self.update_path)

        # nav_layout 추가
        nav_layout = QHBoxLayout()

        nav_container_layout = QVBoxLayout()

        # 전체, 백지, 중복 이미지를 선택하는 위젯
        self.update_image_button = SelectBtns(update_image)
        # 교시, 교사실 번호를 선택하는 위젯
        self.update_image_dropdown = ImageDropDown(update_image)

        nav_container_layout.addWidget(self.update_image_dropdown)
        nav_container_layout.addWidget(self.update_image_button)

        self.scale_slider = ZoomSlider(
            self.update_scale_view)  # 이미지의 크기를 조절하는 위젯

        # nav_layout 위젯 추가
        nav_layout.addLayout(nav_container_layout)
        nav_layout.addStretch(15)
        nav_layout.addWidget(self.scale_slider, 1)

        # header_layout 위젯 추가
        header_layout.addWidget(self.update_folder_button)
        header_layout.addLayout(nav_layout)

    # 폴더 선택, 제출 버튼을 비활성화 시키는 함수
    def toggle_button(self):
        enable = not self.update_folder_button.isEnabled()
        self.toggle_submit_button(enable)
        self.update_folder_button.setEnabled(enable)

    # 지정한 폴더의 이미지가 담긴 폴더만 추출
    def get_image_paths(self):
        depth_data = {}
        max_depth_observed = 0  # 최대 깊이 추적용

        # 지정한 파일의 이미지가 담긴 폴더만 추출
        for root_str, dirs, files in os.walk(self.existing_path):

            try:
                # / 기준으로 경로를 배열로 변경합니다.
                parts_list = list(Path(root_str).parts)
                    
                # 배열로 만든 경로를 기준으로 마지막 3개의 경로만 가져옵니다.
                major_code, class_period, classroom_code = parts_list[-3:]

                parts_tuple = (
                    major_code, class_period, classroom_code)
            except ValueError as e:
                print(e)

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

        return final_processing_list
    
    def calculate_image_position(self, image_path):

        image_crop = ImageCropPanel(image_path)
        result = image_crop.exec()

        if result == QDialog.Accepted:
            print("크롭 완료!")
            print(f"x1={config.x1}, y1={config.y1}, x2={config.x2}, y2={config.y2}")
        else:
            print("사용자가 취소했습니다.")


    # 기본 경로를 저장하는 함수
    def update_path(self):

        # 새로 받을 폴터 경로
        print("이미지 폴터를 선택하고 있습니다.")
        # QFileDialog는 경로를 문자열로 반환합니다.
        new_folder_path_str = QFileDialog.getExistingDirectory(
            self, "이미지 폴더를 선택해주세요")

        if new_folder_path_str:

            # 현재 경로와 다른지 비교
            if self.existing_path != new_folder_path_str:

                # 현재 경로로 지정
                self.existing_path = new_folder_path_str

                final_processing_list = self.get_image_paths()

                # 이미지를 편집하는 위젯
                first_folder_path = Path(final_processing_list[0]["root"])

                first_image_path = None
                for f in first_folder_path.iterdir():
                    if f.is_file() and f.suffix.lower() in config.IMAGE_EXTENSIONS:
                        first_image_path = f
                        break

                self.calculate_image_position(first_image_path)

                # 이미지 전처리를 위한 파라미터 처리
                tasks = []

                for item in final_processing_list:
                    current_root = Path(item["root"])  # 폴더 경로

                    major_code, class_period, classroom_code = item["parts"]
                    json_name = f"{major_code}{class_period}{classroom_code}.json"
                    json_path = current_root / json_name  # json 경로

                    image_paths = ImageProcessor.get_image_paths(
                        current_root)  # 이미지 경로

                    current_root = str(current_root)

                    tasks.append({
                        "root": current_root,
                        "json_path": json_path,
                        "image_paths": image_paths
                    })

                    # json 경로 저장
                    config.json_paths.append(str(json_path))

                self.image_precess(tasks, (config.x1, config.y1, config.x2, config.y2))

                print("이미지 경로 저장 및 불러오기를 완료했습니다.\n")
            else:
                print("선택하신 폴더가 이전의 폴더의 경로와 같습니다.\n")
        else:
            print("이미지 폴더 선택을 취소하셨습니다.\n")

    # 이미지의 전처리를 하는 함수
    def image_precess(self, tasks, crop_rect):
        self._thread = QThreadPool()

        self.runnable = BatchImagePreprocessingRunnable(tasks, crop_rect)

        self.runnable.signals.progress.connect(print)
        self.runnable.signals.error.connect(print)
        self.runnable.signals.result.connect(self.image_save)
        self.runnable.signals.finished.connect(self.is_finish)

        self._thread.start(self.runnable)

    # 스레드가 끝나는 경우 해야하는 작업
    def is_finish(self):
        print("작업이 완료되었습니다.")
        self.update_image_dropdown.update_item(config.json_paths)

    # 전처리한 이미지를 저장하는 함수
    def image_save(self, data):
        output_path = Path(data["output_path"])

        try:
            if output_path.exists():
                output_path.unlink()
        except PermissionError:
            pass
        
        with open(output_path, "wb") as f:
            f.write(data["image_bytes"])
