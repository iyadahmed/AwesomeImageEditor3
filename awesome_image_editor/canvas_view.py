from operator import sub

from PyQt6.QtCore import QPoint, QSize, Qt
from PyQt6.QtGui import QKeyEvent, QMouseEvent, QPainter, QPaintEvent, QPixmap, QTransform, QWheelEvent
from PyQt6.QtWidgets import QWidget

from awesome_image_editor.project import Project


class CanvasView(QWidget):
    def __init__(self, project: Project):
        super().__init__()
        self._project = project

        self._transform = QTransform()

        # Panning
        self.grabKeyboard()
        self._isPanning = False
        self._isSpaceBarHeld = False
        self._panStartPos = QPoint()
        self._panDelta = QPoint()

        # Cached canvas
        self._cached_canvas = QPixmap(project.canvasSize)
        self._cached_canvas.fill(Qt.GlobalColor.transparent)

    @property
    def layers(self):
        return self._project.layers

    @property
    def canvasSize(self):
        return self._project.canvasSize

    def repaintCache(self) -> None:
        self._cached_canvas.fill(Qt.GlobalColor.transparent)

        painter = QPainter()
        painter.begin(self._cached_canvas)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.save()

        for layer in self.layers:
            if layer.isHidden:
                continue
            painter.save()
            layer.draw(painter)
            painter.restore()

        painter.restore()
        painter.end()

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter()
        painter.begin(self)
        painter.fillRect(event.rect(), self.palette().base())

        if not self._cached_canvas.isNull():
            painter.setTransform(self._transform * QTransform.fromTranslate(self._panDelta.x(), self._panDelta.y()))
            painter.drawPixmap(self._cached_canvas.rect(), self._cached_canvas)

        painter.end()

    def calcAllLayersSize(self):
        size = QSize()

        for l in self.layers:
            size = size.expandedTo(l.size())

        return size

    def fitView(self):
        size = self.canvasSize
        if size.width() == 0:
            # Avoid division by zero
            return

        scaledSize = size.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio)
        scale = scaledSize.width() / size.width()

        self._transform = QTransform()
        self._transform.translate(
            self.size().width() / 2 - scaledSize.width() / 2, self.size().height() / 2 - scaledSize.height() / 2
        )
        self._transform.scale(scale, scale)

        self.update()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Space:
            self.setCursor(Qt.CursorShape.OpenHandCursor)
            self._isSpaceBarHeld = True

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Space:
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self._isSpaceBarHeld = False

    def panStart(self, pos: QPoint):
        self._panStartPos = pos
        self._isPanning = True

    def panMove(self, pos: QPoint):
        self._panDelta = sub(pos, self._panStartPos)
        self.update()

    def panEnd(self):
        self._transform *= QTransform.fromTranslate(self._panDelta.x(), self._panDelta.y())
        self._panDelta = QPoint()
        self.update()
        self._isPanning = False

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if (event.buttons() & Qt.MouseButton.LeftButton) and self._isSpaceBarHeld:
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
