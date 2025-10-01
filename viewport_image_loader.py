import math
import os
import cv2
from PySide6.QtWidgets import QWidget, QGraphicsView, QGraphicsScene, QVBoxLayout
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt, QRectF, QThreadPool

from image_calculate_positions_thread import ImageCalculatePositionsThread


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

    def image_center_text_add(self, path):
        filename = os.path.basename(path)

        img = cv2.imread(path)
        if img is None:
            raise FileNotFoundError(f"{path} 파일이 없습니다.")

        h, w, ch = img.shape[:3]

        # 텍스트 설정
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 2
        thickness = 2
        (text_w, text_h), baseline = cv2.getTextSize(
            filename, font, font_scale, thickness)

        center_x = (w - text_w) // 2
        center_y = (h + text_h) // 2  # 왼쪽 아래 기준

        # 중앙 텍스트 삽입
        if (filename != "null_image.jpg"):
            cv2.putText(img, filename, (center_x, center_y),
                        font, font_scale, (0, 0, 0), thickness, cv2.LINE_AA)

        # BGR → RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        qImg = QImage(img_rgb.data, w, h, w*ch, QImage.Format_RGB888)
        return qImg

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
                    qimg = self.image_center_text_add(self.image_paths[i])
                    pixmap = QPixmap.fromImage(qimg).scaledToWidth(
                        self.thumb_width, Qt.SmoothTransformation)
                    item = self.scene.addPixmap(pixmap)
                    item.setPos(x, y)
                    item.setData(0, self.image_paths[i])
                    self.loaded_items[i] = item
                except Exception as e:
                    print(f"이미지 로드 오류: {e}")

    def update_width(self, mode, current_paths):
        if mode == '+':
            self.thumb_width += 100
        elif mode == '-':
            self.thumb_width -= 100

        self.update_images(current_paths)

    def update_images(self, new_paths):
        self.scene.clear()
        self.loaded_items = {}

        self.image_paths = new_paths or ['system/null_image.jpg']
        self.col = len(self.image_paths)

        self.calculate_image_positions()
        self.setup_scene_and_view()
        self.update_visible_images()
