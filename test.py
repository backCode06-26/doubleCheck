from PySide6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsRectItem
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPen, QBrush
import sys


class ResizableRect(QGraphicsRectItem):
    HANDLE_SIZE = 10

    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
        # 아이템 설정
        self.setFlags(
            # 아이템을 마우스로 클릭 가능함
            QGraphicsRectItem.ItemIsSelectable |
            # 아이템을 마우스로 이동 시킬 수 있음
            QGraphicsRectItem.ItemIsMovable
        )
        self.setPen(QPen(Qt.red, 2))  # 외곽선 색 지정
        self.setBrush(QBrush(Qt.transparent))  # 사각형 내부 색 지정
        self.resizing = False
        self.resize_dir = None

    def mousePressEvent(self, event):
        pos = event.pos()  # 마우스 클릭 위치
        rect = self.rect()  # 현재 아이템의 경계 사각형 데이터
        margin = self.HANDLE_SIZE  # 오차 범위

        if (rect.top() + margin <= pos.y() <= rect.top() and
                rect.left() + margin < pos.x() < rect.right() - margin):

            self.resizing = True
            self.resize_dir = "top"

        elif (rect.bottom() - margin <= pos.y() <= rect.bottom() and
                rect.left() + margin < pos.x() < rect.right() - margin):

            self.resizing = True
            self.resize_dir = "bottom"

        elif (rect.right() - margin <= pos.x() <= rect.right() and
              rect.top() + margin < pos.y() < rect.bottom() - margin):

            self.resizing = True
            self.resize_dir = "right"

        elif (rect.left() <= pos.x() <= rect.left() + margin and
              rect.top() + margin < pos.y() < rect.bottom() - margin):

            self.resizing = True
            self.resize_dir = "left"

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
        else:
            self.print_coords()
        super().mouseReleaseEvent(event)

    def print_coords(self):
        rect = self.rect()
        pos = self.pos()
        left = pos.x()
        top = pos.y()
        right = left + rect.width()
        bottom = top + rect.height()
        print(
            f"Left={left:.1f}, Top={top:.1f}, Right={right:.1f}, Bottom={bottom:.1f}")


class GraphicsWindow(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setSceneRect(0, 0, 800, 600)

        rect = ResizableRect(100, 100, 200, 150)
        self.scene.addItem(rect)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GraphicsWindow()
    window.setWindowTitle("Resizable Rectangle Example")
    window.show()
    sys.exit(app.exec())
