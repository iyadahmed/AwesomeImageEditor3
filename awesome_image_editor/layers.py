from abc import ABC, abstractmethod

from PyQt6.QtCore import QSize, QPoint
from PyQt6.QtGui import QImage, QPainter


class Layer(ABC):
    def __init__(self):
        super().__init__()
        self.isHidden = False
        self.isSelected = False
        self.name = ""
        self.location = QPoint(0, 0)

    @abstractmethod
    def draw(self, painter: QPainter):
        pass

    @abstractmethod
    def size(self) -> QSize:
        pass


class ImageLayer(Layer):
    def __init__(self, image: QImage):
        super().__init__()
        self.image = image

    def draw(self, painter: QPainter):
        painter.drawImage(self.image.rect(), self.image)

    def size(self):
        return self.image.size()
