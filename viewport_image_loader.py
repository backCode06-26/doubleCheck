import math
from PySide6.QtWidgets import QWidget, QGraphicsView, QGraphicsScene, QVBoxLayout
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QRectF, QThreadPool

from image_calculate_positions_thread import ImageCalculatePositionsThread


class LazyImageViewer(QWidget):
    def __init__(self, width=200, spacing=10):
        super().__init__()

        self.loaded_items = {}
        self.positions = []

        self.thumb_width = width
        self.spacing = spacing
        self.thread_pool = QThreadPool.globalInstance()

        # layout
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        # Scene & View
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        layout.addWidget(self.view)

        self.view.horizontalScrollBar().valueChanged.connect(self.update_visible_images)

    # positions 재구성
    def calculate_positions(self, new_positions):
        self.positions = new_positions

        is_first = len(self.positions) != 0

        if is_first and new_positions:
            self.update_visible_images()

    # 이미지 위치 계산

    def calculate_image_positions(self):
        self.cal_positions = ImageCalculatePositionsThread(
            self.image_paths, self.thumb_width, self.spacing, self.col)

        self.cal_positions.signals.result.connect(
            lambda postions: self.calculate_positions(postions))

        self.thread_pool.start(self.cal_positions)

    # 이미지 뷰 계산
    def setup_scene_and_view(self):
        total_rows = math.ceil(len(self.image_paths) // self.col)
        self.total_height = total_rows * (self.thumb_width + self.spacing)
        self.scene.setSceneRect(
            0, 0, self.col * (self.thumb_width + self.spacing), self.total_height)

    # 이미지 로드, 현재 보이는 부분만 이미지 로드하는 함수
    def update_visible_images(self):
        rect = self.view.mapToScene(self.view.viewport().rect()).boundingRect()

        for i, (x, y, h) in enumerate(self.positions):
            if i in self.loaded_items:
                continue
            item_rect = QRectF(x, y, self.thumb_width, h)

            if rect.intersects(item_rect):
                pixmap = QPixmap(self.image_paths[i]).scaledToWidth(
                    self.thumb_width, Qt.SmoothTransformation)

                item = self.scene.addPixmap(pixmap)
                item.setPos(x, y)

                self.loaded_items[i] = item

    def update_width(self, mode):
        if (mode == '+'):
            self.thumb_width += 10
        elif (mode == '-'):
            self.thumb_width -= 10

    # 이미지 업데이트
    def update_images(self, new_paths):

        self.scene.clear()
        self.loaded_items = {}

        self.image_paths = new_paths
        self.col = len(self.image_paths)

        if (self.col == 0):
            print("이미지가 존재하지 않습니다.")
            return

        self.calculate_image_positions()
        self.setup_scene_and_view()

        self.update_visible_images()
