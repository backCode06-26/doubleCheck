from PySide6.QtWidgets import QGraphicsScene


class GraphicsScene(QGraphicsScene):
    def mousePressEvent(self, event):
        item = self.itemAt(event.scenePos(), self.views()[0].transform())
        if item:
            print("클릭된 이미지 경로:", item.data(0))
        super().mousePressEvent(event)
