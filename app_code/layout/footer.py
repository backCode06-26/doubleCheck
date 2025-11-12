import os
import config
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton,
)

from PySide6.QtCore import QThreadPool
from app_code._threads.work_thread import ImageProcessRunnable

from app_code.widget.progress import Progress
from app_code.core.data_processor import update_json


class Footer(QWidget):
    def __init__(
        self,
        toggleLayout
    ):
        super().__init__()

        self.toggleLayout = toggleLayout
        self.current_idx = 0
        # 검사 실행에 필요한 값 추출

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
        self.submit_btn = QPushButton("이중 급지 검사")
        self.submit_btn.clicked.connect(self.image_check)
        self.submit_btn.setFixedWidth(150)

        self.multiple_submit_btn = QPushButton("전체 이중 급지 검사")
        self.multiple_submit_btn.clicked.connect(self.image_check_multiple)
        self.multiple_submit_btn.setFixedWidth(150)

        setting_btn = QPushButton("설정")
        setting_btn.clicked.connect(self.toggleLayout)
        setting_btn.setFixedWidth(150)

        # btn_container_layout 위젯 추가
        button_container.addStretch(10)
        button_container.addWidget(self.submit_btn)
        button_container.addWidget(self.multiple_submit_btn)
        button_container.addWidget(setting_btn)
        button_container.addStretch(10)

        # footer_layout 레이아웃 추가
        footer_layout.addLayout(process_layout)
        footer_layout.addLayout(button_container)

    def toggle_submit_button(self, enable):
        self.submit_btn.setEnabled(enable)

    # 백지, 중복 답안 저장 함수
    def save_path(self, image_paths, json_path, mode):

        new_paths = []
        for back_path in image_paths:

            # 받는 이미지는 1은 앞장, 2는 뒷장으로
            # 받은 뒷장을 1로 변경하는 코드입니다.
            back_path = Path(back_path)
            front_path = back_path.with_name(back_path.stem[:-1] + '1' + back_path.suffix)

            current_folder = Path(json_path).parent

            front_path = str(current_folder / front_path)
            back_path = str(current_folder / back_path)

            # 앞장과 뒷장을 배열에 저장합니다.
            new_paths.extend([front_path, back_path])

            # 이미지 경로 저장
            update_json(new_paths, json_path, mode)

    def is_finish(self):
        print("작업이 완료되었습니다.\n")

    # 전체 json을 한번에 검사할 수 있는 함수
    def image_check_multiple(self):
        self.json_paths = config.json_paths

        # 프로그래스 값 초기화
        self.progress.reset()

        # 작업을 이행할 공간 할당
        self.thread_pool = QThreadPool.globalInstance()

        self.run_next_task()

    def run_next_task(self):
        if self.current_idx >= len(self.json_paths):
            print("모든 작업 완료!")
            print(f"전체 작업 시간: {config.all_time:.2f}초")
            return
        
        path = self.json_paths[self.current_idx]
        self.runnable = ImageProcessRunnable(path)

        # 
        self.runnable.signals.progress.connect(lambda msg, p=path: print(f"{p}: {msg}"))
        
        self.runnable.signals.blank_images.connect(lambda lst: self.save_path(lst, path, "blank")) # 백지 답안 저장
        self.runnable.signals.double_images.connect(lambda lst: self.save_path(lst, path, "double")) # 중복 답안 저장
        self.runnable.signals.max_progress.connect(self.progress.progress.setMaximum) # 진행률의 최대값 구하기
        self.runnable.signals.update_progress.connect(self.progress.updateProgress) # 진행률의 값 조작하기

        self.runnable.signals.finished.connect(lambda p=path: print(f"{p} 완료"))
        self.runnable.signals.finished.connect(self.is_finish)

        self.runnable.signals.finished.connect(self.run_next_after)

        self.thread_pool.start(self.runnable)

    def run_next_after(self):
        self.current_idx += 1
        self.run_next_task()

    # 검사 실행 함수
    def image_check(self):
        # 프로그래스 값 초기화
        self.progress.reset()

        # 작업을 이행할 공간 할당
        self.thread_pool = QThreadPool.globalInstance()

        json_path = config.current_json

        if json_path:
            # 작업 준비
            self.current_runnable = ImageProcessRunnable(json_path)

            # 시그널 연결 (.signals를 통해)
            self.current_runnable.signals.progress.connect(print)
            self.current_runnable.signals.blank_images.connect(lambda lst: self.save_path(lst, json_path, "blank"))
            self.current_runnable.signals.double_images.connect(lambda lst: self.save_path(lst, json_path, "double"))
            self.current_runnable.signals.max_progress.connect(self.progress.progress.setMaximum) # 진행률의 최대값 구하기
            self.current_runnable.signals.update_progress.connect(self.progress.updateProgress) # 진행률의 값 조작하기
            self.runnable.signals.finished.connect(self.is_finish)

            # 스레드풀에서 실행
            self.thread_pool.start(self.current_runnable)
        else:
            print("지정된 이미지 데이터가 존재하지 않습니다.")
