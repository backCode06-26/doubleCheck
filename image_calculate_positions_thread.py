from PySide6.QtCore import QObject, Signal, QRunnable, Qt
from PySide6.QtGui import QPixmap


class ImageCalculatePositionsSignals(QObject):
    result = Signal(object)


class ImageCalculatePositionsThread(QRunnable):
    def __init__(self, image_paths, width, spacing, col):
        super().__init__()

        self.image_paths = image_paths
        self.thumb_width = width
        self.spacing = spacing
        self.col = col

        self.signals = ImageCalculatePositionsSignals()

    def run(self):
        positions = []

        x, y = 0, 0
        max_height_in_row = 0

        for i, path in enumerate(self.image_paths):
            pixmap = QPixmap(path).scaledToWidth(
                self.thumb_width, Qt.SmoothTransformation)

            positions.append((x, y, pixmap.height()))
            x += self.thumb_width + self.spacing

            max_height_in_row = max(max_height_in_row, pixmap.height())
            if (i + 1) % self.col == 0:
                x = 0
                y += max_height_in_row + self.spacing

                max_height_in_row = 0
        self.signals.result.emit(positions)
