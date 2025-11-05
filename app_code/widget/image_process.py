from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QImage


class ImageLoader(QObject):
    image_ready = Signal(QImage, int)

    def __init__(self, path, idx):
        super().__init__()
        self.path = path
        self.idx = idx

    def run(self):
        img = QImage(self.path)
        self.image_ready.emit(img, self.idx)
