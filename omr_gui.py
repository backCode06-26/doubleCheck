from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QPushButton, QLabel, QCheckBox,
    QFileDialog, QFrame, QProgressBar
)

from PySide6.QtCore import Qt, QThreadPool
from PySide6.QtGui import QFont

import os

from viewport_image_loader import LazyImageViewer
from work_thread import ImageProcessRunnable

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".bmp")


class omr_gui(QWidget):

    def __init__(self):
        super().__init__()

        self.is_check = False

        self.main_images = []
        self.blank_images = []
        self.double_images = []
        self.current_runnable = None
        self.main_paths = None

        # QWdget 설정
        self.setWindowTitle("OMR 이중 급지")
        self.resize(1000, 800)

        # main_layout 설정
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        # top_layout
        top_layout = QHBoxLayout()

        # right_layout
        right_layout = QVBoxLayout()

        right_title = QLabel("데이터 저장공간")
        right_title.setAlignment(Qt.AlignCenter)
        right_title.setFont(QFont("Arial", 16))

        self.right_scroll = QScrollArea()
        self.right_scroll.setWidgetResizable(True)
        self.right_scroll.setMinimumHeight(300)
        self.right_scroll.setMaximumHeight(1000)

        self.right_container = QWidget()
        self.right_v_layout = QVBoxLayout(self.right_container)
        self.right_scroll.setWidget(self.right_container)

        btn = QPushButton(f"(입력한 답안)")
        btn.clicked.connect(
            lambda: self.update_image(self.main_images))
        self.right_v_layout.addWidget(btn)

        btn = QPushButton(f"(공백 답안)")
        btn.clicked.connect(
            lambda: self.update_image(self.blank_images))
        self.right_v_layout.addWidget(btn)

        btn = QPushButton(f"(중복 답안)")
        btn.clicked.connect(
            lambda: self.update_image(self.double_images))
        self.right_v_layout.addWidget(btn)

        self.right_v_layout.addStretch()

        right_layout.addWidget(right_title)
        right_layout.addWidget(self.right_scroll)

        # left_layout
        left_layout = QVBoxLayout()

        # left_btn
        left_btn = QPushButton("이미지 선택")
        left_btn.clicked.connect(self.select_folder)

        # left_scroll
        self.left_scroll = LazyImageViewer()

        # left_layout 위젯 추가
        left_layout.addWidget(left_btn)
        left_layout.addWidget(self.left_scroll)

        # top_layout layout 추가
        top_layout.addLayout(right_layout, 1)
        top_layout.addLayout(left_layout, 2)

        # main_layout layout 추가
        main_layout.addLayout(top_layout)

        # bottom_layout
        bottom_layout = QVBoxLayout()

        # bottom_top_layout (구분선 레이아웃)
        bt_layout = QHBoxLayout()

        # 위선
        t_line = QFrame()
        t_line.setFrameShape(QFrame.HLine)

        bt_layout.addWidget(t_line)

        # 중간 레이아웃
        btc_layout = QVBoxLayout()

        # 비교 이미지 레이아웃
        btc_sub_t_layout = QHBoxLayout()

        main_title = QLabel("이미지 비교 진행률")
        btc_sub_t_layout.addWidget(main_title)

        self.bt_main_process = QProgressBar()
        # self.bt_main_process.minimumSize(0)
        btc_sub_t_layout.addWidget(self.bt_main_process)

        btc_layout.addLayout(btc_sub_t_layout)

        bt_layout.addLayout(btc_layout)

        # 아래선
        b_line = QFrame()
        b_line.setFrameShape(QFrame.HLine)

        bt_layout.addWidget(b_line)

        # bottom_bottom_layout (프로그램 조작 버튼)
        bb_layout = QHBoxLayout()

        # center
        bb_center_layout = QHBoxLayout()

        # 검사하기 버튼은 main_labels의 값만을 검사하며, main_labels에 들어가는값은
        center_btn = QPushButton("검사하기")
        center_btn.clicked.connect(self.image_progress)

        center_checkbox = QCheckBox("과정 표시")
        center_checkbox.stateChanged.connect(
            lambda state: self.on_checkbox_change(state))

        # center_layout 위젯 추가
        bb_center_layout.addWidget(center_btn)
        bb_center_layout.addWidget(center_checkbox)

        # bottom layout layout 추가
        bb_layout.addStretch(1)
        bb_layout.addLayout(bb_center_layout, 1)
        bb_layout.addStretch(1)

        bottom_layout.addLayout(bt_layout)
        bottom_layout.addLayout(bb_layout)

        # main_layout layout 추가
        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)

    def update_image(self, paths):
        if self.main_paths != paths:
            self.main_paths = paths
            self.left_scroll.update_images(paths)

    # 이미지 선택 함수

    def select_folder(self):
        current_path = QFileDialog.getExistingDirectory(self, "이미지 폴더를 선택해주세요")

        if current_path:
            self.folder_path = current_path

        if self.folder_path:
            # 이미지 파일 경로 가져오기
            self.image_paths = [
                os.path.join(self.folder_path, f)
                for f in os.listdir(self.folder_path)
                if f.lower().endswith(IMAGE_EXTENSIONS)
            ]

            # main_images에 저장
            self.main_images = self.image_paths
            self.blank_images = ["system/null_image.jpg"]
            self.double_images = ["system/null_image.jpg"]

            # 이미지 변경 및 현재 경로 저장
            self.update_image(self.main_images)

    # 백지 저장함수
    def save_image(self, paths, mode="blank"):

        if mode == "blank":
            images = self.blank_images
        elif mode == "double":
            images = self.double_images
        else:
            raise ValueError("mode는 'blank' 또는 'double'이어야 합니다.")

        for path in paths:
            list_path = list(path)
            list_path[6] = '1'
            first_path = "".join(list_path)
            first_path = os.path.join(
                self.folder_path, first_path).replace("\\", "/")
            second_path = os.path.join(
                self.folder_path, path).replace("\\", "/")

            images.append(first_path)
            images.append(second_path)

    def update_progress(self, type):

        process_bar = self.bt_main_process
        current = process_bar.value()

        if (type == 0):
            process_bar.setValue(0)
        elif (type == 1):
            process_bar.setValue(current + 1)

    def last_progress(self):

        process_bar = self.bt_main_process
        current = process_bar.value()
        maxnum = process_bar.maximum()

        process_bar.setValue(current + (maxnum - current))
        print("작업 완료!")

    # 과정표시 체크박스의 함수
    def on_checkbox_change(self, state):

        if state == 2:
            self.is_check = False
        else:
            self.is_check = True

    # 검사 실행 함수

    def image_progress(self):

        self.bt_main_process.setValue(0)

        if self.folder_path:
            self.thread_pool = QThreadPool.globalInstance()

            self.current_runnable = ImageProcessRunnable(
                self.folder_path, batch_size=5)

            self.current_runnable.signals.finished.connect(
                lambda: self.last_progress())

            # 시그널 연결 (.signals를 통해)
            self.current_runnable.signals.progress.connect(
                lambda msg: print(msg))

            self.current_runnable.signals.blank_images.connect(
                lambda lst: self.save_image(lst, "blank"))
            self.current_runnable.signals.double_images.connect(
                lambda lst: self.save_image(lst, "double"))

            # 진행률의 최대값 구하기
            self.current_runnable.signals.max_main_progress.connect(
                lambda c: self.bt_main_process.setMaximum(c))

            # 진행률의 값 조작하기
            self.current_runnable.signals.update_main_progress.connect(
                lambda c: self.update_progress(c))

            # 스레드풀에서 실행
            self.thread_pool.start(self.current_runnable)
        else:
            print("폴더가 지정되지 않았습니다.")
