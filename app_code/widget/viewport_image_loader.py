import math
import os
from PySide6.QtWidgets import QWidget, QGraphicsView, QGraphicsScene, QVBoxLayout, QPushButton, QGraphicsProxyWidget
from PySide6.QtGui import QPixmap, QTransform
from PySide6.QtCore import Qt, QRectF, QThreadPool

from app_code._threads.image_calculate_positions_thread import ImageCalculatePositionsThread


class LazyImageViewer(QWidget):
    def __init__(self, width=600, spacing=10):
        super().__init__()

        self.thumb_width = width
        self.spacing = spacing
        self.loaded_items = {}
        self.positions = []

        self.thread_pool = QThreadPool.globalInstance()
        self.image_paths = []
        self.col = 1

        # 레이아웃
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        # Scene & View
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        layout.addWidget(self.view)

        self.view.horizontalScrollBar().valueChanged.connect(self.update_visible_images)

    def calculate_positions(self, new_positions):
        self.positions = new_positions
        if self.positions:
            self.update_visible_images()

    def calculate_image_positions(self):
        if not hasattr(self, 'image_paths') or not self.image_paths:
            return

        self.cal_positions = ImageCalculatePositionsThread(
            self.image_paths, self.thumb_width, self.spacing, self.col)

        self.cal_positions.signals.result.connect(
            lambda positions: self.calculate_positions(positions))

        self.thread_pool.start(self.cal_positions)

    def setup_scene_and_view(self):
        if not self.image_paths:
            return

        total_rows = math.ceil(len(self.image_paths) / self.col)
        self.total_height = total_rows * \
            ((self.thumb_width + 250) + self.spacing)
        self.scene.setSceneRect(
            0, 0, self.col * (self.thumb_width + self.spacing), self.total_height)

    def update_visible_images(self):
        if not hasattr(self, 'positions') or not self.positions:
            return

        rect = self.view.mapToScene(self.view.viewport().rect()).boundingRect()

        for i, (x, y, h) in enumerate(self.positions):
            if i in self.loaded_items:
                continue

            item_rect = QRectF(x, y, self.thumb_width, h)
            if rect.intersects(item_rect):
                try:
                    image_path = self.image_paths[i]

                    pixmap = QPixmap(image_path).scaledToWidth(
                        self.thumb_width, Qt.SmoothTransformation
                    )
                    item = self.scene.addPixmap(pixmap)
                    item.setPos(x, y)
                    item.setData(0, image_path)
                    self.loaded_items[i] = item

                    filename = os.path.basename(image_path)
                    if filename == "null_image.JPG":
                        return

                    btn = QPushButton("뷰어")
                    proxy = QGraphicsProxyWidget()
                    proxy.setWidget(btn)
                    proxy.setParentItem(item)
                    proxy.setPos(self.thumb_width - 100, 10)

                    btn.clicked.connect(
                        lambda checked, path=image_path: os.startfile(path))
                except Exception as e:
                    print(f"이미지 로드 오류: {e}")

    def scaleView(self, factor):
        t = QTransform()
        t.scale(factor, factor)
        self.view.setTransform(t)

    def loadImage(self, new_paths):
        self.scene.clear()
        self.loaded_items = {}

        self.image_paths = new_paths
        self.col = len(self.image_paths)

        self.calculate_image_positions()
        self.setup_scene_and_view()
        self.update_visible_images()
