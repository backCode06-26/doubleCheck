from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt, Signal, QRect, QPoint
from PySide6.QtGui import QPainter, QColor, QPen

class CropLabel(QLabel):
    """이미지 위에 드래그/크기 조절 가능한 크롭 박스"""

    cropChanged = Signal(tuple)  # x1, y1, x2, y2 (원본 이미지 좌표)
    HANDLE_SIZE = 10

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.image = None
        self.pixmap_scaled = None
        self.scale_factor = 1.0

        self.rect = QRect(50, 50, 200, 150)  # 초기 크롭 박스
        self.dragging = False
        self.resizing = False
        self.resize_dir = None
        self.start_pos = QPoint()

    def setImage(self, pixmap_scaled, scale_factor=1.0):
        self.pixmap_scaled = pixmap_scaled
        self.scale_factor = scale_factor
        self.setPixmap(self.pixmap_scaled)
        self.resize(self.pixmap_scaled.size())

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.rect:
            return
        painter = QPainter(self)
        pen = QPen(QColor(255, 0, 0), 2)
        painter.setPen(pen)
        painter.drawRect(self.rect)

        painter.setBrush(QColor(255, 0, 0))
        for handle in self.handles():
            painter.drawRect(handle)

    def handles(self):
        r = self.rect
        s = self.HANDLE_SIZE
        mid_x = r.left() + r.width() // 2
        mid_y = r.top() + r.height() // 2
        return [
            QRect(r.left() - s//2, r.top() - s//2, s, s),  # top-left
            QRect(mid_x - s//2, r.top() - s//2, s, s),    # top-middle
            QRect(r.right() - s//2, r.top() - s//2, s, s),# top-right
            QRect(r.right() - s//2, mid_y - s//2, s, s),  # right-middle
            QRect(r.right() - s//2, r.bottom() - s//2, s, s),  # bottom-right
            QRect(mid_x - s//2, r.bottom() - s//2, s, s),      # bottom-middle
            QRect(r.left() - s//2, r.bottom() - s//2, s, s),   # bottom-left
            QRect(r.left() - s//2, mid_y - s//2, s, s)         # left-middle
        ]

    def mousePressEvent(self, event):
        pos = event.pos()
        for idx, handle in enumerate(self.handles()):
            if handle.contains(pos):
                self.resizing = True
                self.resize_dir = idx
                self.start_pos = pos
                return
        if self.rect.contains(pos):
            self.dragging = True
            self.start_pos = pos

    def mouseMoveEvent(self, event):
        pos = event.pos()
        if self.dragging:
            delta = pos - self.start_pos
            self.rect.translate(delta)
            self.rect = self.rect.intersected(QRect(0, 0, self.width(), self.height()))
            self.start_pos = pos
            self.update()
            self.emitCropCoords()
        elif self.resizing:
            self.resizeRect(pos)
            self.update()
            self.emitCropCoords()
        else:
            cursor = Qt.ArrowCursor
            for handle in self.handles():
                if handle.contains(pos):
                    cursor = Qt.SizeAllCursor
            if self.rect.contains(pos):
                cursor = Qt.SizeAllCursor
            self.setCursor(cursor)

    def mouseReleaseEvent(self, event):
        self.dragging = False
        self.resizing = False
        self.resize_dir = None

    def resizeRect(self, pos):
        r = self.rect
        idx = self.resize_dir
        if idx == 0: r.setTopLeft(pos)
        elif idx == 1: r.setTop(pos.y())
        elif idx == 2: r.setTopRight(pos)
        elif idx == 3: r.setRight(pos.x())
        elif idx == 4: r.setBottomRight(pos)
        elif idx == 5: r.setBottom(pos.y())
        elif idx == 6: r.setBottomLeft(pos)
        elif idx == 7: r.setLeft(pos.x())
        self.rect = r.intersected(QRect(0, 0, self.width(), self.height()))

    def emitCropCoords(self):
        x1 = int(self.rect.left() * self.scale_factor)
        y1 = int(self.rect.top() * self.scale_factor)
        x2 = int(self.rect.right() * self.scale_factor)
        y2 = int(self.rect.bottom() * self.scale_factor)
        self.cropChanged.emit((x1, y1, x2, y2))
