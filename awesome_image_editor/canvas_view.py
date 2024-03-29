from _operator import sub
from operator import sub
from typing import Optional

from PyQt6.QtCore import QPoint, QSize, Qt
from PyQt6.QtGui import QKeyEvent, QMouseEvent, QPainter, QPaintEvent, QPixmap, QTransform, QWheelEvent
from PyQt6.QtWidgets import QWidget

from awesome_image_editor.project_model import ProjectModel
from awesome_image_editor.canvas_tools.canvas_toolbar import CanvasToolBar


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
    def __init__(self, parent: QWidget, project: ProjectModel, toolsToolBar: CanvasToolBar):
        super().__init__(parent)
        self._project = project
        self._toolsToolBar = toolsToolBar

        self._transform = QTransform()

        # Panning
        self.grabKeyboard()
        self._isPanning = False
        self._isSpaceBarHeld = False
        self._panStartPos = QPoint()
        self._panDelta = QPoint()

        # Cached canvas
        self._cachedCanvas = QPixmap(project.canvasSize)
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

    def panToolMousePress(self, event: QMouseEvent):
        if event.buttons() & Qt.MouseButton.LeftButton:
            if self._isSpaceBarHeld:
                pos = event.pos()
                self._panStartPos = pos
                self._isPanning = True
                return True
        return False

    def panToolMouseMove(self, event: QMouseEvent):
        if self._isPanning:
            pos = event.pos()
            self._panDelta = sub(pos, self._panStartPos)
            self.update()
            return True
        return False

    def panToolMouseRelease(self, event: QMouseEvent):
        if self._isPanning:
            self._transform *= QTransform.fromTranslate(self._panDelta.x(), self._panDelta.y())
            self._panDelta = QPoint()
            self.update()
            self._isPanning = False
            return True
        return False

    def panToolKeyPress(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Space:
            self.setCursor(Qt.CursorShape.OpenHandCursor)
            self._isSpaceBarHeld = True
            return True
        return False

    def panToolKeyRelease(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Space:
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self._isSpaceBarHeld = False
            return True
        return False

    @property
    def canvasSize(self):
        return self._project.canvasSize

    def repaintCache(self) -> None:
        self._cachedCanvas.fill(Qt.GlobalColor.transparent)

        painter = QPainter()
        painter.begin(self._cachedCanvas)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        for layer in self._project.iterLayersBackToFront():
            if layer.isHidden:
                continue
            painter.save()
            painter.translate(layer.location)
            layer.draw(painter)
            painter.restore()

        painter.end()

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter()
        painter.begin(self)
        painter.fillRect(event.rect(), self.palette().base())

        if not self._cachedCanvas.isNull():
            transform = self._transform * QTransform.fromTranslate(self._panDelta.x(), self._panDelta.y())
            painter.setTransform(transform)
            painter.save()
            # Transform is set before setClipRect to correctly represent the canvas rectangle when panning and zooming
            painter.setClipRect(self._cachedCanvas.rect())
            # We reset transform so that checkerboard pattern scale doesn't change when user zooms in/out
            painter.resetTransform()
            translation = QPoint(int(transform.dx()), int(transform.dy()))
            # Pattern is moved by negative translation to align top left corner with canvas's top left corner
            painter.drawTiledPixmap(self._cachedCanvas.rect(), CHECKERBOARD_PATTERN_PIXMAP, -1 * translation)
            painter.restore()
            painter.drawPixmap(self._cachedCanvas.rect(), self._cachedCanvas)

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
        if not self.panToolKeyPress(event):
            self._toolsToolBar.getCurrentTool().keyPress(event)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        if not self.panToolKeyRelease(event):
            self._toolsToolBar.getCurrentTool().keyRelease(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if not self.panToolMousePress(event):
            self._toolsToolBar.getCurrentTool().mousePress(event, self._transform, self._project)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if not self.panToolMouseMove(event):
            self._toolsToolBar.getCurrentTool().mouseMove(event, self._transform, self._project)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if not self.panToolMouseRelease(event):
            self._toolsToolBar.getCurrentTool().mouseRelease(event, self._transform, self._project)

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
