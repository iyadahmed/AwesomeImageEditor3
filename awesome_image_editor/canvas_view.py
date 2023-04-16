from operator import sub
from typing import Optional

from PyQt6.QtCore import QPoint, QSize, Qt
from PyQt6.QtGui import QKeyEvent, QMouseEvent, QPainter, QPaintEvent, QPixmap, QTransform, QWheelEvent
from PyQt6.QtWidgets import QWidget

from awesome_image_editor.project_model import ProjectModel


def createCheckerBoardTile(sideLength: int):
    pixmap = QPixmap(sideLength, sideLength)
    painter = QPainter()
    painter.begin(pixmap)
    painter.fillRect(0, 0, 8, 8, Qt.GlobalColor.white)
    painter.fillRect(8, 8, 16, 16, Qt.GlobalColor.white)
    painter.fillRect(8, 0, 16, 8, Qt.GlobalColor.gray)
    painter.fillRect(0, 8, 8, 16, Qt.GlobalColor.gray)
    painter.end()
    return pixmap


CHECKERBOARD_PATTERN_PIXMAP = createCheckerBoardTile(16)


class CanvasView(QWidget):
    def __init__(self, parent: QWidget, project: ProjectModel):
        super().__init__(parent)
        self._project = project

        self._transform = QTransform()

        # Panning
        self.grabKeyboard()
        self._isPanning = False
        self._isSpaceBarHeld = False
        self._panStartPos = QPoint()
        # TODO: get rid of panDelta
        self._panDelta = QPoint()

        # Cached canvas
        self._cached_canvas = QPixmap(project.canvasSize)
        self.repaintCache()

        # Connect signals
        def onLayersModify():
            self.repaintCache()
            self.update()

        project.layersAdded.connect(onLayersModify)
        project.layersDeleted.connect(onLayersModify)
        project.layersOrderChanged.connect(onLayersModify)
        project.layersVisibilityChanged.connect(onLayersModify)

        self._lastMousePos: Optional[QPoint] = None

    @property
    def canvasSize(self):
        return self._project.canvasSize

    def repaintCache(self) -> None:
        self._cached_canvas.fill(Qt.GlobalColor.transparent)

        painter = QPainter()
        painter.begin(self._cached_canvas)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.save()

        for layer in self._project.iterLayersBackToFront():
            if layer.isHidden:
                continue
            painter.save()
            painter.translate(layer.location)
            layer.draw(painter)
            painter.restore()

        painter.restore()
        painter.end()

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter()
        painter.begin(self)
        painter.fillRect(event.rect(), self.palette().base())

        if not self._cached_canvas.isNull():
            transform = self._transform * QTransform.fromTranslate(self._panDelta.x(), self._panDelta.y())
            painter.setTransform(transform)
            painter.save()
            # Transform is set before setClipRect to correctly represent the canvas rectangle when panning and zooming
            painter.setClipRect(self._cached_canvas.rect())
            # We reset transform so that checkerboard pattern scale doesn't change when user zooms in/out
            painter.resetTransform()
            translation = QPoint(int(transform.dx()), int(transform.dy()))
            # Pattern is moved by negative translation to align top left corner with canvas's top left corner
            painter.drawTiledPixmap(self._cached_canvas.rect(), CHECKERBOARD_PATTERN_PIXMAP, -1 * translation)
            painter.restore()
            painter.drawPixmap(self._cached_canvas.rect(), self._cached_canvas)

        painter.end()

    def calcAllLayersSize(self):
        size = QSize()

        for layer in self._project.iterLayersBackToFront():
            size = size.expandedTo(layer.size())

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
        if event.buttons() & Qt.MouseButton.LeftButton:
            if self._isSpaceBarHeld:
                self.panStart(event.pos())
            else:
                canvasInverseTransform = self._transform.inverted()[0]
                self._lastMousePos = canvasInverseTransform.map(event.pos())

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._isPanning:
            self.panMove(event.pos())

        elif self._lastMousePos is not None:
            canvasInverseTransform = self._transform.inverted()[0]
            currentMousePos = canvasInverseTransform.map(event.pos())
            delta = currentMousePos - self._lastMousePos
            self._lastMousePos = currentMousePos

            for layer in self._project.iterLayersBackToFront():
                if layer.isSelected:
                    layer.location += delta

            self.repaintCache()
            self.update()

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
