import os
import sys
import config

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QGraphicsScene
)
from PySide6.QtGui import QIcon

from code.widget.viewport_image_loader import LazyImageViewer
from code.layout.sub_container import SubContainer

from code.layout.header import Header
from code.layout.footer import Footer


class omr_gui(QWidget):

    def __init__(self):
        super().__init__()

        if getattr(sys, "frozen", False):
            current_path = os.path.dirname(os.path.abspath(sys.executable))
        else:
            current_path = os.path.dirname(os.path.abspath(__file__))
        window_icon = os.path.join(
            current_path, "images", "icon", "double_check_icon.ico")
        
        self.current_mode = ""

        # QWdget 설정
        self.setWindowTitle("OMR 이중 급지")
        self.resize(1500, 1200)

        self.setWindowIcon(QIcon(window_icon))

        # body_layout 레이아웃
        body_layout = QHBoxLayout()

        # main_layout 설정
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        # 이미지 로더, 이미지 로더의 함수를 사용하기 위해서 먼저 생성함
        self.image_loader = LazyImageViewer()
        self.view = QGraphicsScene(self.image_loader.scene)

        header_layout = Header(
            self.updateImage,
            self.image_loader.scaleView
        )

        # section_layout 추가
        section_layout = QVBoxLayout()

        # section_layout 위젯 추가
        section_layout.addWidget(self.image_loader)

        container = SubContainer()

        footer_layout = Footer(container.toggleLayout)

        # main_container_layout 추가
        main_layout.addWidget(header_layout)
        main_layout.addLayout(section_layout)
        main_layout.addWidget(footer_layout)

        # body_layout 레이아웃, 위젯 추가
        body_layout.addLayout(main_layout)
        body_layout.addWidget(container)

        self.setLayout(body_layout)

    # 이미지를 변경하는 함수
    def updateImage(self, mode="main"):
        """
            현재 이미지의 경로와 변경된 이미지의 경로를 확인하여
            다른 경우에만 작동시켜 처리 시간을 줄입니다.
        """
        if self.current_mode != mode:

            # 현재 경로를 변경된 경로로 변경합니다.
            self.current_mode = mode

            current_image = config.current_json[mode]
            self.image_loader.loadImage(current_image)
