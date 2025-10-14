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
from .zoom_in_btn import ZoomInBtn
import core.folder_processing as fp


class omr_gui(QWidget):

    def __init__(self):
        super().__init__()

        self.is_check = False

        self.main_images = []
        self.blank_images = []
        self.double_images = []

        self.existing_path = ""
        self.folder_path = ""
        self.current_runnable = None
        self.main_paths = []

        self.toggle = False

        # QWdget 설정
        self.setWindowTitle("OMR 이중 급지")
        self.resize(1500, 1200)

        # main_layout 레이아웃
        main_layout = QHBoxLayout()

        # right_section_layout 설정
        main_right_layout = QVBoxLayout()
        main_right_layout.setContentsMargins(20, 20, 20, 20)
        main_right_layout.setSpacing(10)

        # main_section_layout 설정
        top_layout = QVBoxLayout()

        # header_layout 추가
        top_t_layout = QVBoxLayout()

        # top_t_r_btn 추가
        top_t_t_btn = QPushButton("폴더를 선택해주세요")
        top_t_t_btn.setStyleSheet("padding: 5px 8px; font-size: 16px;")
        top_t_t_btn.clicked.connect(self.select_folder)

        # nav_layout 추가
        top_t_b_layout = QHBoxLayout()

        self.top_t_b_btn = SelectBtns(self.change_images)
        self.top_t_b_zoom_btn = ZoomInBtn()

        top_t_b_layout.addWidget(self.top_t_b_btn, 6)
        top_t_b_layout.addStretch(15)
        top_t_b_layout.addWidget(self.top_t_b_zoom_btn, 1)

        top_t_layout.addWidget(top_t_t_btn)
        top_t_layout.addLayout(top_t_b_layout)

        # section_layout 추가
        top_b_layout = QVBoxLayout()

        # top_b_layout_scroll 추가
        self.top_b_layout_scroll = LazyImageViewer()
        self.view = QGraphicsScene(self.top_b_layout_scroll.scene)

        # left_layout 위젯 추가
        top_b_layout.addWidget(self.top_b_layout_scroll)

        # top_layout layout 추가
        top_layout.addLayout(top_t_layout)
        top_layout.addLayout(top_b_layout)

        # main_right_layout layout 추가
        main_right_layout.addLayout(top_layout)

        # footer_layout
        bottom_layout = QVBoxLayout()

        # footer_process_layout (프로그레스 바 레이아웃)
        footer_process_layout = QHBoxLayout()

        # 프로그레스 바 관련 라벨
        main_title = QLabel("이미지 비교 진행률")

        # 프로그레스 바
        self.main_process = QProgressBar()
        self.main_process.setMinimum(1)
        self.main_process.setMaximum(100)

        footer_process_layout.addWidget(main_title)
        footer_process_layout.addWidget(self.main_process)

        # btn_controll_layout (프로그램 조작 버튼)
        bb_layout = QHBoxLayout()

        # btn_container_layout
        bb_center_layout = QHBoxLayout()

        # 검사하기 버튼은 main_labels의 값만을 검사하며, main_labels에 들어가는값은
        center_submit_btn = QPushButton("이중 급지 검사")
        center_submit_btn.clicked.connect(self.image_progress)
        center_submit_btn.setFixedWidth(150)

        center_setting_btn = QPushButton("설정")
        center_setting_btn.clicked.connect(
            lambda: self.toggle_main_left_layout(self.main_left_layout))
        center_setting_btn.setFixedWidth(150)

        # center_checkbox = QCheckBox("과정 표시")
        # center_checkbox.stateChanged.connect(
        #     lambda state: self.on_checkbox_change(state))

        # center_layout 위젯 추가
        bb_center_layout.addWidget(center_submit_btn)
        bb_center_layout.addWidget(center_setting_btn)

        # bottom layout layout 추가
        bb_layout.addStretch(1)
        bb_layout.addLayout(bb_center_layout, 1)
        bb_layout.addStretch(1)

        bottom_layout.addLayout(footer_process_layout)
        bottom_layout.addLayout(bb_layout)

        # main_right_layout layout 추가
        main_right_layout.addLayout(bottom_layout)

        # left_section_layout
        container = QWidget()
        container.setMaximumWidth(250)
        container.setMaximumWidth(150)

        # sub_section_layout 레이아웃
        self.main_left_layout = QVBoxLayout()
        try:
            main_left_all_lebal = QLabel("전체 답안 수")
            self.main_left_all_btn = QPushButton("전체 답안 보기")
            self.main_left_all_btn.clicked.connect(
                lambda: os.startfile(self.existing_path))
            self.main_left_all_count = QLabel("0 장")

            main_left_blank_lebal = QLabel("백지 답안 수")
            self.main_left_blank_btn = QPushButton("백지 답안 보기")
            self.main_left_blank_btn.clicked.connect(
                lambda: os.startfile(os.path.join(self.existing_path, "blank")))
            self.main_left_blank_count = QLabel("0 장")

            main_left_double_lebal = QLabel("중복 답안 수")
            self.main_left_double_btn = QPushButton("중복 답안 보기")
            self.main_left_double_btn.clicked.connect(
                lambda: os.startfile(os.path.join(self.existing_path, "double")))
            self.main_left_double_count = QLabel("0 장")
        except Exception:
            print("이중 급지를 판단하기 위한 폴터를 선택해주세요")

        # 기준이 되는 Hash값을 받기 위한 입력폼
        self.hash_slider = ValueSlider()

        # 레이아웃에 추가
        self.main_left_layout.addStretch(1)
        self.main_left_layout.addWidget(main_left_all_lebal)
        self.main_left_layout.addWidget(self.main_left_all_btn)
        self.main_left_layout.addWidget(self.main_left_all_count)
        self.main_left_layout.addStretch(2)

        self.main_left_layout.addWidget(main_left_blank_lebal)
        self.main_left_layout.addWidget(self.main_left_blank_btn)
        self.main_left_layout.addWidget(self.main_left_blank_count)
        self.main_left_layout.addStretch(2)

        self.main_left_layout.addWidget(main_left_double_lebal)
        self.main_left_layout.addWidget(self.main_left_double_btn)
        self.main_left_layout.addWidget(self.main_left_double_count)
        self.main_left_layout.addStretch(2)

        self.main_left_layout.addWidget(self.hash_slider)

        self.main_left_layout.addStretch(12)

        container.setLayout(self.main_left_layout)

        main_layout.addLayout(main_right_layout)
        main_layout.addWidget(container)

        self.setLayout(main_layout)

    def set_main_paths(self, paths):
        self.main_images = paths

        main_images_count = len(self.main_images)
        self.main_left_all_count.setText(f"{main_images_count} 장")

    def set_blank_paths(self, paths):
        self.blank_images = paths

        blank_images_count = len(self.blank_images)
        self.main_left_blank_count.setText(f"{blank_images_count} 장")

    def set_double_paths(self, paths):
        self.double_images = paths

        double_images_count = len(self.double_images)
        self.main_left_double_count.setText(f"{double_images_count} 장")

    def toggle_main_left_layout(self, layout):
        for i in range(layout.count()):
            item = layout.itemAt(i)
            widget = item.widget()
            if widget:
                if self.toggle == False:
                    widget.hide()

                elif self.toggle == True:
                    widget.show()

        self.toggle = True if not self.toggle else False

    # 이미지를 변경하는 함수
    def update_image(self, paths):
        """
            현재 이미지의 경로와 변경된 이미지의 경로를 확인하여
            다른 경우에만 작동시켜 처리 시간을 줄입니다.
        """
        if self.main_paths != paths:

            # 현재 경로를 변경된 경로로 변경합니다.
            self.main_paths = paths

            def update_func(paths):
                self.top_b_layout_scroll.update_images(paths)

            update_func(paths)

    def change_images(self, mode):
        images = {
            "all": self.main_images,
            "blank": self.blank_images,
            "double": self.double_images
        }
        self.update_image(images[mode])

    # 받은 폴더의 경로로 이미지의 경로를 만드는 함수
    def select_folder(self):
        # 새로 받을 폴터 경로
        self.new_folder_path = QFileDialog.getExistingDirectory(
            self, "이미지 폴더를 선택해주세요")

        if self.new_folder_path:
            # 현재 폴더 경로와 새로 받은 폴더 경로가 다른 경우에만 새로 시작합니다.
            if self.existing_path != self.new_folder_path:
                # 새로운 경로 선택
                self.existing_path = self.new_folder_path

                # 폴더 초기화, 중복, 백지 폴더 생성
                fp.folder_processing(self.existing_path)

                # 받은 폴더 경로로 이미지의 경로들을 만듭니다.
                # IMAGE_EXTENSIONS의 허용된 확장자를 가진 이미지만 허용하게 합니다.
                IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".bmp")
                self.image_paths = [
                    os.path.join(self.new_folder_path, f)
                    for f in os.listdir(self.new_folder_path)
                    if f.lower().endswith(IMAGE_EXTENSIONS)
                ]

                if not self.image_paths:
                    print("선택한 폴더에 이미지가 없습니다.")
                    return

                # main_images에 저장
                self.set_main_paths(self.image_paths)

                self.top_t_b_btn.on_first_button_clicked()

                # 이미지 변경 및 현재 경로 저장
                self.update_image(self.main_images)

    # def update_image_width(self, mode):
    #     self.top_b_layout_scroll.update_width(mode, self.main_images)

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
        if mode == "blank":

            # 백지 답안 처리
            self.set_blank_paths(new_paths)
            fp.image_copys(self.existing_path, "blank", new_paths)
        elif mode == "double":

            # 중복 답안 처리
            self.set_double_paths(new_paths)
            fp.image_copys(self.existing_path, "double", new_paths)
        else:
            raise ValueError("mode는 'blank' 또는 'double'이어야 합니다.")

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

    # 과정표시 체크박스의 함수
    # def on_checkbox_change(self, state):

    #     if state == 2:
    #         self.is_check = False
    #     else:
    #         self.is_check = True

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
                lambda cnt: self.bt_main_process.setMaximum(cnt))

            # 진행률의 값 조작하기
            self.current_runnable.signals.update_main_progress.connect(
                lambda cnt: self.update_progress(cnt))

            self.current_runnable.signals.finished.connect(
                lambda: self.last_progress())

            # 스레드풀에서 실행
            self.thread_pool.start(self.current_runnable)
        else:
            print("폴더가 지정되지 않았습니다.")
