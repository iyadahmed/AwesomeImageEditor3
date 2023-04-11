from pathlib import Path
from typing import Optional, Union

from PyQt6.QtCore import QPoint, QPointF, QRect, QRectF, QSize, Qt, pyqtSignal
from PyQt6.QtGui import QBrush, QMouseEvent, QPainter, QPaintEvent, QPixmap, QWheelEvent, QResizeEvent
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import QApplication, QWidget

from awesome_image_editor.project import Project

THUMBNAIL_SIZE = QSize(64, 64)
EYE_ICON_WIDTH = EYE_ICON_HEIGHT = 20
MARGIN = 10


def pixmapFromSVG(filepath: Path, size: QSize, tint: Optional[QBrush] = None):
    pixmap = QPixmap(size)
    pixmap.fill(Qt.GlobalColor.transparent)
    renderer = QSvgRenderer(filepath.as_posix())
    painter = QPainter()
    painter.begin(pixmap)
    renderer.render(painter, QRectF(QPointF(0, 0), size.toSizeF()))

    if not (tint is None):
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        painter.fillRect(pixmap.rect(), tint)

    painter.end()
    return pixmap


ICON_HIDDEN_PIXMAP = pixmapFromSVG(Path(__file__).parent / "icons/layers/hidden.svg", THUMBNAIL_SIZE)
ICON_HIDDEN_HIGHLIGHT_PIXMAP = pixmapFromSVG(
    Path(__file__).parent / "icons/layers/hidden.svg", THUMBNAIL_SIZE, QApplication.palette().highlightedText()
)

ICON_VISIBLE_PIXMAP = pixmapFromSVG(Path(__file__).parent / "icons/layers/visible.svg", THUMBNAIL_SIZE)
ICON_VISIBLE_HIGHLIGHT_PIXMAP = pixmapFromSVG(
    Path(__file__).parent / "icons/layers/visible.svg", THUMBNAIL_SIZE, QApplication.palette().highlightedText()
)


def clamp(value, lower, upper):
    if value > upper:
        return upper

    if value < lower:
        return lower

    return value


class TreeView(QWidget):
    layersVisibilityChanged = pyqtSignal()
    layersSelectionChanged = pyqtSignal()
    layersDeleted = pyqtSignal()
    layersOrderChanged = pyqtSignal()

    def __init__(self, project: Project):
        super().__init__()
        self._project = project

        self._scrollPos = 0

        self.layersDeleted.connect(lambda: self.updateScrollPos(0))
        self.layersOrderChanged.connect(lambda: self.updateScrollPos(0))

    @property
    def layers(self):
        return self._project.layers

    def deleteSelected(self):
        # TODO: improve memory usage? a copy of list is made and filtered,
        #       so it uses more memory for a moment,
        #       also it is done anyways even if there are no selected layers
        new_layers = [layer for layer in self.layers if not layer.isSelected]
        self.layers.clear()
        self.layers.extend(new_layers)
        self.update()
        self.layersDeleted.emit()

    def raiseSelectedLayers(self):
        for i in range(len(self.layers) - 1)[::-1]:
            if self.layers[i].isSelected and (not self.layers[i + 1].isSelected):
                self.layers[i], self.layers[i + 1] = self.layers[i + 1], self.layers[i]

        self.update()
        self.layersOrderChanged.emit()

    def lowerSelectedLayers(self):
        for i in range(len(self.layers) - 1):
            if self.layers[i + 1].isSelected and (not self.layers[i].isSelected):
                self.layers[i], self.layers[i + 1] = self.layers[i + 1], self.layers[i]

        self.update()
        self.layersOrderChanged.emit()

    def calcItemsScreenHeight(self):
        # TODO: change this logic when we have groups (layers is not a list anymore but a tree),
        #       or when items have different height
        return THUMBNAIL_SIZE.height() * len(self.layers)

    def calcMaxScrollPos(self):
        """Calculate the scroll position needed to make the very bottom item visible without excess,
        if the widget height is already enough to display all items it returns 0 (no need to scroll) """
        if self.height() >= self.calcItemsScreenHeight():
            return 0
        return self.calcItemsScreenHeight() - self.height()

    def updateScrollPos(self, scrollDelta: Union[int, float]):
        self._scrollPos = clamp(self._scrollPos - scrollDelta, 0, self.calcMaxScrollPos())

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
        self.update()

    def deselectAll(self):
        for layer in self.layers:
            layer.isSelected = False

    def findItemUnderPosition(self, pos: QPoint):
        y = -self._scrollPos
        x = 0
        for layer in self.layers[::-1]:
            if y < pos.y() < (y + THUMBNAIL_SIZE.height()):
                eyeIconRect = QRectF(
                    x,
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
            self.layersVisibilityChanged.emit()
        else:
            if event.buttons() & Qt.MouseButton.LeftButton:
                if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                    layer.isSelected = not layer.isSelected
                else:
                    self.deselectAll()
                    layer.isSelected = True

        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter()
        painter.begin(self)

        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        painter.fillRect(event.rect(), self.palette().window())
        painter.save()

        painter.translate(0, -1 * self._scrollPos)

        x = 0
        y = 0

        for layer in self.layers[::-1]:
            treeItemRect = QRect(x, y, self.size().width(), THUMBNAIL_SIZE.height())

            if layer.isSelected:
                painter.fillRect(treeItemRect, self.palette().highlight())

            eyeIconRect = QRect(
                x,
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
                    x + EYE_ICON_WIDTH + MARGIN,
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
                x + EYE_ICON_WIDTH + MARGIN + THUMBNAIL_SIZE.width() + MARGIN,
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
