from PySide6.QtWidgets import (
    QApplication, QGraphicsView, QGraphicsScene, QGraphicsRectItem,
    QGraphicsPixmapItem, QPushButton, QVBoxLayout, QWidget
)
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPen, QBrush, QPixmap, QImage
import sys
import cv2
import config
from app_code.core.rotate_correction import correct_skew


class ResizableRect(QGraphicsRectItem):
    HANDLE_SIZE = 10

    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
        self.setFlags(
            QGraphicsRectItem.ItemIsSelectable |
            QGraphicsRectItem.ItemIsMovable
        )
        self.setPen(QPen(Qt.red, 2))
        self.setBrush(QBrush(Qt.transparent))
        self.resizing = False
        self.resize_dir = None
        self.print_coords()

    def mousePressEvent(self, event):
        pos = event.pos()
        rect = self.rect()
        margin = self.HANDLE_SIZE

        if rect.right() <= pos.x() <= rect.right() + margin and rect.bottom() - margin <= pos.y() <= rect.bottom():
            self.resizing = True
            self.resize_dir = "bottom_left"
        else:
            self.resizing = False
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.resizing:
            new_pos = event.pos()
            rect = QRectF(self.rect().topLeft(), new_pos)
            self.setRect(rect)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.resizing:
            self.resizing = False
        self.print_coords()
        super().mouseReleaseEvent(event)

    def get_coords(self):
        """좌표를 딕셔너리 형태로 반환"""
        rect = self.rect()
        pos = self.pos()
        left = pos.x()
        top = pos.y()
        right = left + rect.width()
        bottom = top + rect.height()
        return {"left": left, "top": top, "right": right, "bottom": bottom}

    def print_coords(self):
        c = self.get_coords()
        print(
            f"Left={c['left']:.1f}, Top={c['top']:.1f}, Right={c['right']:.1f}, Bottom={c['bottom']:.1f}")


class GraphicsWindow(QWidget):
    def __init__(self, image_path):
        super().__init__()
        self.view = QGraphicsView()
        self.scene = QGraphicsScene(self.view)
        self.view.setScene(self.scene)
        self.view.setSceneRect(0, 0, 800, 600)

        # 버튼 추가
        self.save_button = QPushButton("좌표 저장")
        self.save_button.clicked.connect(self.save_coords)

        # 레이아웃
        layout = QVBoxLayout(self)
        layout.addWidget(self.view)
        layout.addWidget(self.save_button)

        # 이미지 추가
        if image_path:

            img = cv2.imread(image_path)
            correct_img = correct_skew(img)
            rgb_img = cv2.cvtColor(correct_img, cv2.COLOR_BGR2RGB)

            h, w, ch = rgb_img.shape
            new_w = w // 2
            new_h = h // 2

            resize_img = cv2.resize(
                rgb_img,
                (new_w, new_h),
                interpolation=cv2.INTER_LINEAR
            )

            h, w, ch = resize_img.shape
            bytes_per_line = ch * w

            q_image = QImage(
                resize_img.data,
                w,
                h,
                bytes_per_line,
                QImage.Format.Format_RGB888
            )

            pixmap = QPixmap.fromImage(q_image)

            self.image_item = QGraphicsPixmapItem(pixmap)

            width = self.image_item.pixmap().width()
            height = self.image_item.pixmap().height()

            center_x_offset = -width / 8.0
            center_y_offset = -height / 4.0

            self.image_item.setOffset(center_x_offset, center_y_offset)

            self.scene.addItem(self.image_item)

        # 사각형 추가
        self.rect_item = ResizableRect(
            center_x_offset, center_y_offset, 250, 250)
        self.scene.addItem(self.rect_item)

    def save_coords(self):
        """현재 사각형 좌표를 config에 저장"""
        c = self.rect_item.get_coords()

        # config에 저장
        config.top = c["top"]
        config.bottom = c["bottom"]
        config.right = c["right"]
        config.left = c["left"]

        print("\n 좌표 저장 완료!")
        print(
            f"left={config.left}, top={config.top}, right={config.right}, bottom={config.bottom}")

        self.close()
