import os
import config

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, 
)

from PySide6.QtCore import QThreadPool
from code._threads.work_thread import ImageProcessRunnable

from code.widget.progress import Progress
from code.core.data_processor import saveJson

class Footer(QWidget):
    def __init__(
            self,
            toggleLayout
        ):
        super().__init__()

        self.toggleLayout = toggleLayout
        # 검사 실행에 필요한 값 추출
        self.json_content = config.current_json # json 내용

        self.folder_path = config.FOLDER_PATH # 폴더 경로
        self.hash_value = config.hash_value # 해쉬값
        self.core_value = config.core_count # 코어 개수

        # self.current_runnable = None

         # footer_layout
        footer_layout = QVBoxLayout(self)

        # process_layout (프로그레스 바 레이아웃)
        process_layout = QHBoxLayout()

        # 프로그레스 바 관련 라벨
        title = QLabel("이미지 비교 진행률")

        self.progress = Progress()

        # process_layout 위젯 추가
        process_layout.addWidget(title)
        process_layout.addWidget(self.progress)

        # btn_container_layout
        button_container = QHBoxLayout()

        # 검사하기 버튼은 main_labels의 값만을 검사하며, main_labels에 들어가는값은
        submit_btn = QPushButton("이중 급지 검사")
        submit_btn.clicked.connect(self.imageCheck)
        submit_btn.setFixedWidth(150)

        setting_btn = QPushButton("설정")
        setting_btn.clicked.connect(self.toggleLayout)
        setting_btn.setFixedWidth(150)

        # btn_container_layout 위젯 추가
        button_container.addStretch(10)
        button_container.addWidget(submit_btn)
        button_container.addWidget(setting_btn)
        button_container.addStretch(10)

        # footer_layout 레이아웃 추가
        footer_layout.addLayout(process_layout)
        footer_layout.addLayout(button_container)

    def changePath(self, image_path):
        change_path = os.path.join(
            self.folder_path, image_path).replace("\\", "/")
        return change_path

        # 백지, 중복 답안 저장 함수
    def savePath(self, paths, mode):

        new_paths = []
        for path in paths:

            # 받는 이미지는 1은 앞장, 2는 뒷장으로
            # 받은 뒷장을 1로 변경하는 코드입니다.
            name, ext = os.path.splitext(path)
            first_path = name[:-1] + '1' + ext

            first_path = self.changePath(first_path)
            second_path = self.changePath(path)

            # 앞장과 뒷장을 배열에 저장합니다.
            new_paths.extend([first_path, second_path])

            # 이미지 경로 저장
            saveJson(new_paths, mode)

        folder_path = os.path.join(self.folder_path, mode)
        print(
            f"{"백지" if mode == "blank" else "중복"} 답지의 경로 저장, {folder_path}에 이미지를 저장합니다.\n")


    # 검사 실행 함수
    def imageCheck(self):
        # 프로그래스 값 초기화
        self.progress.reset()

        if self.folder_path:

            # 작업을 이행할 공간 할당
            self.thread_pool = QThreadPool.globalInstance()

            # 작업 준비
            self.current_runnable = ImageProcessRunnable(
                self.folder_path, self.hash_value, batch_size=5)

            # 시그널 연결 (.signals를 통해)
            self.current_runnable.signals.progress.connect(
                lambda msg: print(msg))

            self.current_runnable.signals.blank_images.connect(
                lambda lst: self.savePath(lst, "blank"))
            self.current_runnable.signals.double_images.connect(
                lambda lst: self.savePath(lst, "double"))

            # # 진행률의 최대값 구하기
            # self.current_runnable.signals.max_main_progress.connect(
            #     lambda cnt: self.process.setMaximum(cnt))

            # # 진행률의 값 조작하기
            # self.current_runnable.signals.update_main_progress.connect(
            #     lambda cnt: self.update_progress(cnt))

            self.current_runnable.signals.finished.connect(lambda: print("작업을 완료했습니다."))

            # 스레드풀에서 실행
            self.thread_pool.start(self.current_runnable)
        else:
            print("폴더가 지정되지 않았습니다.")