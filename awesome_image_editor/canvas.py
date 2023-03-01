from abc import ABC, abstractmethod

from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtGui import QImage, QMouseEvent, QPainter, QPaintEvent, QWheelEvent
from PyQt6.QtWidgets import QWidget


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
        self._offsetStartPos = QPoint()
        self._deltaOffset = QPoint()
        self._offset = QPoint()

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.save()
        painter.translate(self._offset + self._deltaOffset)
        for layer in self.layers:
            painter.save()
            layer.draw(painter)
            painter.restore()
        painter.restore()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.buttons() & Qt.MouseButton.MiddleButton:
            self._offsetStartPos = event.pos()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if event.buttons() & Qt.MouseButton.MiddleButton:
            self._deltaOffset = event.pos() - self._offsetStartPos
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.MiddleButton:
            self._offset = self._deltaOffset + self._offset
            self._deltaOffset = QPoint()
            self.update()
