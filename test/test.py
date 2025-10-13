from PySide6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QPushButton, QGraphicsProxyWidget, QVBoxLayout, QWidget, QLabel, QDialog
from PySide6.QtGui import QPixmap, QPainter
from PySide6.QtCore import Qt
import sys

class ImageViewer(QDialog):
    """이미지 전체를 보여주는 뷰어"""
    def __init__(self, pixmap):
        super().__init__()
        self.setWindowTitle("Image Viewer")
        layout = QVBoxLayout(self)
        label = QLabel()
        label.setPixmap(pixmap.scaled(800, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        layout.addWidget(label)
        self.resize(800, 600)

class GraphicsImageScene(QGraphicsScene):
    def __init__(self, image_paths):
        super().__init__()
        self.image_paths = image_paths
        self.load_images()

    def load_images(self):
        x_offset = 0
        for path in self.image_paths:
            pixmap = QPixmap(path)
            item = QGraphicsPixmapItem(pixmap)
            item.setPos(x_offset, 0)
            self.addItem(item)

            # 이미지 오른쪽 위에 버튼 추가
            button = QPushButton("열기")
            button_proxy = QGraphicsProxyWidget()
            button_proxy.setWidget(button)
            button_proxy.setParentItem(item)  # pixmap 위에 올리기
            button_proxy.setPos(pixmap.width() - 60, 10)  # 오른쪽 위 위치

            # 버튼 클릭 시 뷰어 열기
            button.clicked.connect(lambda checked, p=pixmap: self.open_viewer(p))

            x_offset += pixmap.width() + 20  # 다음 이미지 위치

    def open_viewer(self, pixmap):
        viewer = ImageViewer(pixmap)
        viewer.exec()

if __name__ == "__main__":
    folder_path = r"C:\Users\유호진\Pictures\Test3_같은 답안지를 중복으로 넣어봄(통과)"
    import os
    paths = [os.path.join(folder_path, f)
             for f in os.listdir(folder_path)
             if f.lower().endswith((".jpg", ".jpeg", ".png"))]

    app = QApplication(sys.argv)
    scene = GraphicsImageScene(paths)
    view = QGraphicsView(scene)
    view.setRenderHint(QPainter.SmoothPixmapTransform)
    view.resize(1000, 600)
    view.show()
    sys.exit(app.exec())
