from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPaintEvent, QImage

from abc import ABC, abstractmethod


class Layer(ABC):
    @abstractmethod
    def draw(self, painter: QPainter):
        pass


class ImageLayer(Layer):
    def __init__(self, image: QImage):
        self.image = image

    def draw(self, painter: QPainter):
        painter.drawImage(self.image.rect(), self.image)


class CanvasWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layers: list[Layer] = []

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        for layer in self.layers:
            painter.save()
            layer.draw(painter)
            painter.restore()
