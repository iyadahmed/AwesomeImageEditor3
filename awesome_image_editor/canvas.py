from abc import ABC, abstractmethod
from operator import add, sub

from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtGui import QImage, QKeyEvent, QMouseEvent, QPainter, QPaintEvent, QTransform, QWheelEvent
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

        self._transform = QTransform()

        # Panning
        self.grabKeyboard()
        self._isPanning = False
        self._isSpaceBarHeld = False
        self._panStartPos = QPoint()
        self._panDelta = QPoint()

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.save()
        painter.setTransform(self._transform * QTransform.fromTranslate(self._panDelta.x(), self._panDelta.y()))
        for layer in self.layers:
            painter.save()
            layer.draw(painter)
            painter.restore()
        painter.restore()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Space:
            self._isSpaceBarHeld = True

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Space:
            self._isSpaceBarHeld = False

    def panStart(self, pos: QPoint):
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self._panStartPos = pos
        self._isPanning = True

    def panMove(self, pos: QPoint):
        self._panDelta = sub(pos, self._panStartPos)
        self.update()

    def panEnd(self):
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self._transform *= QTransform.fromTranslate(self._panDelta.x(), self._panDelta.y())
        self._panDelta = QPoint()
        self.update()
        self._isPanning = False

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if (event.buttons() & Qt.MouseButton.MiddleButton) or (
            (event.buttons() & Qt.MouseButton.LeftButton) and self._isSpaceBarHeld
        ):
            self.panStart(event.pos())

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._isPanning:
            self.panMove(event.pos())

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self._isPanning:
            self.panEnd()

    def wheelEvent(self, event: QWheelEvent) -> None:
        if event.modifiers() & Qt.KeyboardModifier.AltModifier:
            scale = 1.1
            if event.angleDelta().x() < 0:
                scale = 0.9

            zoomingPoint = event.position()
            deltaTransform = QTransform()
            deltaTransform.translate(zoomingPoint.x(), zoomingPoint.y())
            deltaTransform.scale(scale, scale)
            deltaTransform.translate(-zoomingPoint.x(), -zoomingPoint.y())

            self._transform *= deltaTransform

            self.update()
            event.accept()
