import math
import os
import cv2
import numpy as np
from pathlib import Path
from PySide6.QtWidgets import QWidget, QGraphicsView, QGraphicsScene, QVBoxLayout, QPushButton, QGraphicsProxyWidget
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt, QRectF, QThreadPool
from PIL import Image, ImageDraw, ImageFont

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

    # 이미지 이름 추가
    def image_center_text_add(self, path):
        filename = os.path.basename(path)
        image_path = Path(path)

        with open(image_path, "rb") as f:
            file_bytes = np.asarray(bytearray(f.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        if img is None:
            raise FileNotFoundError(f"{path} 파일이 없습니다.")
        
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img_rgb)
        draw = ImageDraw.Draw(pil_img)

        # 한글 폰트
        font_path = "system/BATANG.TTC"
        font = ImageFont.truetype(font_path, 30)

        # textbbox로 텍스트 크기 계산
        bbox = draw.textbbox((0, 0), filename, font=font)  # (x1, y1, x2, y2)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        # 중앙 위치
        img_w, img_h = pil_img.size
        position = ((img_w - text_w)//2, (img_h - text_h)//2)

        # 텍스트 삽입
        draw.text(position, filename, font=font, fill=(0, 0, 0))

        # 다시 QImage로 변환
        img_np = np.array(pil_img)
        h, w, ch = img_np.shape
        qimg = QImage(img_np.data, w, h, w*ch, QImage.Format_RGB888)
        return qimg
    
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

                    btn = QPushButton("뷰어")
                    proxy = QGraphicsProxyWidget()
                    proxy.setWidget(btn)
                    proxy.setParentItem(item)
                    proxy.setPos(self.thumb_width -100, 10)

                    btn.clicked.connect(lambda: os.startfile(self.image_paths[i]))
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
