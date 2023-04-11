from pathlib import Path
from typing import Optional, Union

from PyQt6.QtCore import QPoint, QPointF, QRect, QRectF, QSize, Qt, pyqtSignal
from PyQt6.QtGui import QBrush, QMouseEvent, QPainter, QPaintEvent, QPixmap, QWheelEvent, QResizeEvent, QIcon
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import QApplication, QWidget

from awesome_image_editor.project_model import ProjectModel

THUMBNAIL_SIZE = QSize(64, 64)
EYE_ICON_WIDTH = EYE_ICON_HEIGHT = 20
MARGIN = 5


def getTintedPixmap(pixmap: QPixmap, tint: Optional[QBrush]):
    tintedPixmap = pixmap.copy()
    painter = QPainter()
    painter.begin(tintedPixmap)
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
    painter.fillRect(tintedPixmap.rect(), tint)
    painter.end()
    return tintedPixmap


ICON_HIDDEN_PIXMAP = QIcon((Path(__file__).parent / "icons/layers/hidden.svg").as_posix()).pixmap(
    QSize(EYE_ICON_WIDTH, EYE_ICON_HEIGHT))
ICON_HIDDEN_HIGHLIGHT_PIXMAP = getTintedPixmap(ICON_HIDDEN_PIXMAP, QApplication.palette().highlightedText())

ICON_VISIBLE_PIXMAP = QIcon((Path(__file__).parent / "icons/layers/visible.svg").as_posix()).pixmap(
    QSize(EYE_ICON_WIDTH, EYE_ICON_HEIGHT))
ICON_VISIBLE_HIGHLIGHT_PIXMAP = getTintedPixmap(ICON_VISIBLE_PIXMAP, QApplication.palette().highlightedText())


def clamp(value, lower, upper):
    if value > upper:
        return upper

    if value < lower:
        return lower

    return value


class TreeView(QWidget):
    def __init__(self, project: ProjectModel):
        super().__init__()
        self._project = project

        self._scrollPos = 0

        # Needed to get mouse move events without user clicking left mouse button
        # (for example, it is needed for setting mouse pointer based on location in widget)
        self.setMouseTracking(True)

        # Connect signals
        project.layersAdded.connect(lambda: self.updateScrollPos(0))
        project.layersDeleted.connect(lambda: self.updateScrollPos(0))
        project.layersOrderChanged.connect(lambda: self.update())
        project.layersVisibilityChanged.connect(lambda: self.update())
        project.layersSelectionChanged.connect(lambda: self.update())

    @property
    def project(self):
        return self._project

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if event.pos().y() < (self.calcItemsScreenHeight() - self._scrollPos):
            if self.cursor() != Qt.CursorShape.PointingHandCursor:
                self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            if self.cursor() != Qt.CursorShape.ArrowCursor:
                self.setCursor(Qt.CursorShape.ArrowCursor)

        event.accept()

    def calcItemsScreenHeight(self):
        # TODO: change this logic when we have groups (layers is not a list anymore but a tree),
        #       or when items have different height
        return sum(THUMBNAIL_SIZE.height() for _ in self._project.iterLayersFrontToBack())

    def calcMaxScrollPos(self):
        """Calculate the scroll position needed to make the very bottom item visible without excess,
        if the widget height is already enough to display all items it returns 0 (no need to scroll) """
        if self.height() >= self.calcItemsScreenHeight():
            return 0
        return self.calcItemsScreenHeight() - self.height()

    def updateScrollPos(self, scrollDelta: Union[int, float]):
        self._scrollPos = clamp(self._scrollPos - scrollDelta, 0, self.calcMaxScrollPos())
        self.update()

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.updateScrollPos(0)
        super().resizeEvent(event)

    def wheelEvent(self, event: QWheelEvent) -> None:
        numPixels = event.pixelDelta()
        angleDelta = event.angleDelta()

        if not numPixels.isNull():
            scrollDelta = numPixels.y()
        else:
            scrollDelta = (angleDelta.y() / 15) * 4

        if self.height() < self.calcItemsScreenHeight():
            # Only scroll if height is not enough to display all items
            self.updateScrollPos(scrollDelta)

        event.accept()

    def findItemUnderPosition(self, pos: QPoint):
        y = -self._scrollPos
        x = 0
        for layer in self._project.iterLayersFrontToBack():
            if y < pos.y() < (y + THUMBNAIL_SIZE.height()):
                eyeIconRect = QRectF(
                    x + MARGIN,
                    y + THUMBNAIL_SIZE.height() / 2 - EYE_ICON_HEIGHT / 2,
                    EYE_ICON_WIDTH,
                    EYE_ICON_HEIGHT,
                )
                layerUnderMouse = layer
                return layerUnderMouse, eyeIconRect
            y += THUMBNAIL_SIZE.height()

        return None, None

    def mousePressEvent(self, event: QMouseEvent) -> None:
        layer, eyeIconRect = self.findItemUnderPosition(event.position())
        if layer is None:
            return

        if eyeIconRect.contains(event.position()):
            # Toggle hidden state
            layer.isHidden = not layer.isHidden
            self.project.layersVisibilityChanged.emit()
        else:
            if event.buttons() & Qt.MouseButton.LeftButton:
                if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                    layer.isSelected = not layer.isSelected
                else:
                    self._project.deselectAll()
                    layer.isSelected = True
                self.project.layersSelectionChanged.emit()

        event.accept()

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter()
        painter.begin(self)

        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        painter.fillRect(event.rect(), self.palette().window())
        painter.save()

        painter.translate(0, -1 * self._scrollPos)

        x = 0
        y = 0

        for layer in self._project.iterLayersFrontToBack():
            treeItemRect = QRect(x, y, self.size().width(), THUMBNAIL_SIZE.height())

            if layer.isSelected:
                painter.fillRect(treeItemRect, self.palette().highlight())

            eyeIconRect = QRect(
                x + MARGIN,
                y + THUMBNAIL_SIZE.height() // 2 - EYE_ICON_HEIGHT // 2,
                EYE_ICON_WIDTH,
                EYE_ICON_HEIGHT,
            )

            # Determine eye icon based on hide and selection states of the layer
            if layer.isSelected:
                eyeIconPixmap = ICON_HIDDEN_HIGHLIGHT_PIXMAP if layer.isHidden else ICON_VISIBLE_HIGHLIGHT_PIXMAP
            else:
                eyeIconPixmap = ICON_HIDDEN_PIXMAP if layer.isHidden else ICON_VISIBLE_PIXMAP

            painter.drawPixmap(eyeIconRect, eyeIconPixmap)

            layerSize = layer.size()

            if layerSize.width() > 0:
                thumbnailRect = QRectF(
                    x + MARGIN + EYE_ICON_WIDTH + MARGIN,
                    y,
                    THUMBNAIL_SIZE.width(),
                    THUMBNAIL_SIZE.height(),
                )

                scaledSize = layerSize.scaled(THUMBNAIL_SIZE, Qt.AspectRatioMode.KeepAspectRatio)

                painter.save()
                painter.translate(
                    thumbnailRect.center().x() - scaledSize.width() / 2,
                    thumbnailRect.center().y() - scaledSize.height() / 2,
                )
                scale = scaledSize.width() / layerSize.width()
                painter.scale(scale, scale)
                layer.draw(painter)
                painter.restore()

            layerNameRect = QRect(
                x + MARGIN + EYE_ICON_WIDTH + MARGIN + THUMBNAIL_SIZE.width() + MARGIN,
                y,
                self.size().width(),
                THUMBNAIL_SIZE.height(),
            )
            painter.save()
            if layer.isSelected:
                painter.setPen(QApplication.palette().highlightedText().color())
            painter.drawText(layerNameRect, Qt.AlignmentFlag.AlignVCenter, layer.name)
            painter.restore()

            y += THUMBNAIL_SIZE.height()

        painter.restore()
        painter.end()
