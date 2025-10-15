from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSlider,
    QPushButton, QLabel,
    QFileDialog, QFrame, QProgressBar,
    QGraphicsScene
)

from PySide6.QtCore import Qt, QThreadPool
from PySide6.QtGui import QFont

import os

from thread.work_thread import ImageProcessRunnable
from .viewport_image_loader import LazyImageViewer
from .value_slider import ValueSlider
from .select_btns import SelectBtns
from .zoom_slider import ZoomSlider
from .viewer_count_btn import ViewerCountBtn
import core.folder_processing as fp


class omr_gui(QWidget):

    def __init__(self):
        super().__init__()

        self.images = {
            "main": [r"code\system\null_image.JPG"],
            "blank": [r"code\system\null_image.JPG"],
            "double": [r"code\system\null_image.JPG"]
        }
        self.current_mode = ""
        self.existing_path = None

        self.toggle = False

        self.current_runnable = None

        # QWdget 설정
        self.setWindowTitle("OMR 이중 급지")
        self.resize(1500, 1200)

        # body_layout 레이아웃
        body_layout = QHBoxLayout()

        # main_layout 설정
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        # header_layout 추가
        header_layout = QVBoxLayout()

        # 폴더 경로를 선택하는 GUI
        folder_select_btn = QPushButton("폴더를 선택해주세요")
        folder_select_btn.setStyleSheet("padding: 5px 8px; font-size: 16px;")
        folder_select_btn.clicked.connect(self.select_folder)

        # nav_layout 추가
        nav_layout = QHBoxLayout()

        # 이미지 로더, 이미지 로더의 함수를 사용하기 위해서 먼저 생성함
        self.image_loader = LazyImageViewer()
        self.view = QGraphicsScene(self.image_loader.scene)

        # 전체, 중복, 백지 답안을 보여주는 토글 버튼
        self.image_change_btn = SelectBtns(self.update_image)
        self.zoom_slider = ZoomSlider(self.image_loader.scale_view)

        # section_layout 추가
        section_layout = QVBoxLayout()

        # footer_layout
        footer_layout = QVBoxLayout()

        # process_layout (프로그레스 바 레이아웃)
        process_layout = QHBoxLayout()

        # 프로그레스 바 관련 라벨
        main_title = QLabel("이미지 비교 진행률")

        # 프로그레스 바
        self.main_process = QProgressBar()
        self.main_process.setMinimum(1)
        self.main_process.setMaximum(100)

        # btn_container_layout
        btn_container_layout = QHBoxLayout()

        # 검사하기 버튼은 main_labels의 값만을 검사하며, main_labels에 들어가는값은
        submit_btn = QPushButton("이중 급지 검사")
        submit_btn.clicked.connect(self.image_progress)
        submit_btn.setFixedWidth(150)

        setting_btn = QPushButton("설정")
        setting_btn.clicked.connect(
            lambda: self.toggle_sub_layout(self.sub_layout))
        setting_btn.setFixedWidth(150)

        # nav_layout 위젯 추가
        nav_layout.addWidget(self.image_change_btn, 6)
        nav_layout.addStretch(15)
        nav_layout.addWidget(self.zoom_slider, 1)

        # header_layout 위젯 추가
        header_layout.addWidget(folder_select_btn)
        header_layout.addLayout(nav_layout)

        # section_layout 위젯 추가
        section_layout.addWidget(self.image_loader)

        # process_layout 위젯 추가
        process_layout.addWidget(main_title)
        process_layout.addWidget(self.main_process)

        # btn_container_layout 위젯 추가
        btn_container_layout.addStretch(10)
        btn_container_layout.addWidget(submit_btn)
        btn_container_layout.addWidget(setting_btn)
        btn_container_layout.addStretch(10)

        # footer_layout 레이아웃 추가
        footer_layout.addLayout(process_layout)
        footer_layout.addLayout(btn_container_layout)

        # main_container_layout 추가
        main_layout.addLayout(header_layout)
        main_layout.addLayout(section_layout)
        main_layout.addLayout(footer_layout)

        # sub_container
        sub_container = QWidget()
        sub_container.setMaximumWidth(250)
        sub_container.setMaximumWidth(150)

        # sub_layout 레이아웃
        self.sub_layout = QVBoxLayout()
        try:
            self.main_viewer_count_btn = ViewerCountBtn(
                self, "main")
            self.blank_viewer_count_btn = ViewerCountBtn(
                self, "blank")
            self.double_viewer_count_btn = ViewerCountBtn(
                self, "double")
        except Exception:
            print("이중 급지를 판단하기 위한 폴터를 선택해주세요")

        # 기준이 되는 Hash값을 받기 위한 입력폼
        self.hash_slider = ValueSlider()

        # sub_layout 위젯 추가
        self.sub_layout.addStretch(1)
        self.sub_layout.addWidget(self.main_viewer_count_btn)
        self.sub_layout.addStretch(2)

        self.sub_layout.addWidget(self.blank_viewer_count_btn)
        self.sub_layout.addStretch(2)

        self.sub_layout.addWidget(self.double_viewer_count_btn)
        self.sub_layout.addStretch(2)

        self.sub_layout.addWidget(self.hash_slider)
        self.sub_layout.addStretch(12)

        # sub_container 레이아웃 추가
        sub_container.setLayout(self.sub_layout)

        # body_layout 레이아웃, 위젯 추가
        body_layout.addLayout(main_layout)
        body_layout.addWidget(sub_container)

        self.setLayout(body_layout)

    # 파일의 배열를 변경하는 함수
    def change_paths(self, paths, mode="main"):
        self.images[mode] = paths

        total = len(paths)

        viewer_count_btns = {
            "main": self.main_viewer_count_btn,
            "blank": self.blank_viewer_count_btn,
            "double": self.double_viewer_count_btn,
        }
        viewer_count_btns[mode].setLabel(total)

    # 이미지를 변경하는 함수
    def update_image(self, mode="main"):
        """
            현재 이미지의 경로와 변경된 이미지의 경로를 확인하여
            다른 경우에만 작동시켜 처리 시간을 줄입니다.
        """
        if self.current_mode != mode:

            # 현재 경로를 변경된 경로로 변경합니다.
            self.current_mode = mode

            self.image_loader.update_images(
                self.images[self.current_mode])

    def toggle_sub_layout(self, layout):
        for i in range(layout.count()):
            item = layout.itemAt(i)
            widget = item.widget()
            if widget:
                if self.toggle == False:
                    widget.hide()

                elif self.toggle == True:
                    widget.show()

        self.toggle = True if not self.toggle else False

    # 받은 폴더의 경로로 이미지의 경로를 만드는 함수
    def select_folder(self):
        # 새로 받을 폴터 경로
        print("이미지 폴터를 선택하고 있습니다.")
        self.new_folder_path = QFileDialog.getExistingDirectory(
            self, "이미지 폴더를 선택해주세요")

        if self.new_folder_path:
            # 현재 폴더 경로와 새로 받은 폴더 경로가 다른 경우에만 새로 시작합니다.
            if self.existing_path != self.new_folder_path:
                # 새로운 경로 선택
                self.existing_path = self.new_folder_path

                # 받은 폴더 경로로 이미지의 경로들을 만듭니다.
                # IMAGE_EXTENSIONS의 허용된 확장자를 가진 이미지만 허용하게 합니다.

                print("폴더 안 이미지의 경로 가져오는 중입니다.")
                IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".bmp")
                self.image_paths = [
                    os.path.join(self.existing_path, f)
                    for f in os.listdir(self.existing_path)
                    if f.lower().endswith(IMAGE_EXTENSIONS)
                ]

                # 이미지가 존재하는지 확인합니다.
                if not self.image_paths:
                    print("선택한 폴더에 이미지가 없습니다.")
                    return

                # 폴더 초기화, 중복, 백지 폴더 생성
                fp.folder_processing(self.existing_path)
                print("백지, 중복 답안을 저장할 폴더를 구성하고 있습니다.")

                # main_images에 저장
                self.change_paths(self.image_paths, "main")

                # 이미지 변경 및 현재 경로 저장
                self.update_image("main")
                print("이미지 경로 저장 및 불러오기를 완료했습니다.\n")
            else:
                print("선택하지 폴더가 이전의 폴더의 경로와 같습니다.\n")
        else:
            print("이미지 폴더 선택을 취소하셨습니다.\n")

    # 백지, 중복 답안 저장 함수
    def save_image(self, paths, mode):

        def change_func(image_path):
            change_path = os.path.join(
                self.existing_path, image_path).replace("\\", "/")
            return change_path

        new_paths = []
        for path in paths:

            # 받는 이미지는 1은 앞장, 2는 뒷장으로
            # 받은 뒷장을 1로 변경하는 코드입니다.
            name, ext = os.path.splitext(path)
            first_path = name[:-1] + '1' + ext

            first_path = change_func(first_path)
            second_path = change_func(path)

            # 앞장과 뒷장을 배열에 저장합니다.
            new_paths.append(first_path)
            new_paths.append(second_path)

        # 모드에 따라서 저장한 배열을 따로 지정합니다.
        fp.image_copys(self.existing_path, mode, new_paths)
        self.change_paths(new_paths, mode)

        folder_path = os.path.join(self.existing_path, mode)
        print(
            f"{"백지" if mode == "blank" else "중복"} 답지의 경로 저장, {folder_path}에 이미지를 저장합니다.\n")

    # 프로그레스 바 증가 함수
    def update_progress(self, type):

        process_bar = self.main_process
        current = process_bar.value()

        if (type == 0):
            process_bar.setValue(0)
        elif (type == 1):
            process_bar.setValue(current + 1)

    # 프로그레스 바 마지막 처리 함수
    def last_progress(self):

        process_bar = self.main_process
        current = process_bar.value()
        maxnum = process_bar.maximum()

        process_bar.setValue(current + (maxnum - current))
        print("작업 완료!")

    # 검사 실행 함수
    def image_progress(self):
        self.main_process.setValue(0)
        # 현재 기준 hash 반환
        hash_value = self.hash_slider.get_hash_value()

        if self.existing_path:
            self.thread_pool = QThreadPool.globalInstance()

            self.current_runnable = ImageProcessRunnable(
                self.existing_path, hash_value, batch_size=5)

            # 시그널 연결 (.signals를 통해)
            self.current_runnable.signals.progress.connect(
                lambda msg: print(msg))

            self.current_runnable.signals.blank_images.connect(
                lambda lst: self.save_image(lst, "blank"))
            self.current_runnable.signals.double_images.connect(
                lambda lst: self.save_image(lst, "double"))

            # 진행률의 최대값 구하기
            self.current_runnable.signals.max_main_progress.connect(
                lambda cnt: self.main_process.setMaximum(cnt))

            # 진행률의 값 조작하기
            self.current_runnable.signals.update_main_progress.connect(
                lambda cnt: self.update_progress(cnt))

            self.current_runnable.signals.finished.connect(
                lambda: self.last_progress())

            # 스레드풀에서 실행
            self.thread_pool.start(self.current_runnable)
        else:
            print("폴더가 지정되지 않았습니다.")
