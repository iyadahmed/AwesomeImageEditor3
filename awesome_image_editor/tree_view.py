from typing import Optional, Union

from PyQt6.QtCore import QPoint, QRect, QSize, Qt
from PyQt6.QtGui import QBrush, QMouseEvent, QPainter, QPaintEvent, QPixmap, QResizeEvent, QWheelEvent, QPalette
from PyQt6.QtWidgets import QApplication, QWidget

from awesome_image_editor.icons import getIcon
from awesome_image_editor.layers import Layer
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


ICON_HIDDEN_PIXMAP = getIcon("layers/hidden.svg").pixmap(QSize(EYE_ICON_WIDTH, EYE_ICON_HEIGHT))
ICON_HIDDEN_HIGHLIGHT_PIXMAP = getTintedPixmap(ICON_HIDDEN_PIXMAP, QApplication.palette().highlightedText())

ICON_VISIBLE_PIXMAP = getIcon("layers/visible.svg").pixmap(QSize(EYE_ICON_WIDTH, EYE_ICON_HEIGHT))
ICON_VISIBLE_HIGHLIGHT_PIXMAP = getTintedPixmap(ICON_VISIBLE_PIXMAP, QApplication.palette().highlightedText())


def clamp(value, lower, upper):
    if value > upper:
        return upper

    if value < lower:
        return lower

    return value


class TreeViewItem:
    def __init__(self, x: int, y: int, layer: Layer, width: int, height: int, palette: QPalette):
        self.x = x
        self.y = y
        self.layer = layer
        self.width = width
        self.height = height
        self.palette = palette

    def containsYPos(self, y: float):
        return self.y < y < (self.y + self.height)

    def eyeIconRect(self):
        return QRect(
            self.x + MARGIN,
            self.y + self.height // 2 - EYE_ICON_HEIGHT // 2,
            EYE_ICON_WIDTH,
            EYE_ICON_HEIGHT,
        )

    def thumbnailRect(self):
        return QRect(
            self.x + MARGIN + EYE_ICON_WIDTH + MARGIN,
            self.y,
            THUMBNAIL_SIZE.width(),
            THUMBNAIL_SIZE.height(),
        )

    def layerNameRect(self):
        return QRect(
            self.x + MARGIN + EYE_ICON_WIDTH + MARGIN + THUMBNAIL_SIZE.width() + MARGIN,
            self.y,
            self.width,
            self.height,
        )

    def rect(self):
        return QRect(self.x, self.y, self.width, self.height)

    def drawBackground(self, painter: QPainter):
        if self.layer.isSelected:
            # Background rectangle is expanded by 1 pixel to ensure no gaps due to implicit conversion to QRectF when
            # passed to fillRect
            painter.fillRect(self.rect(), self.palette.highlight())

    def drawEyeIcon(self, painter: QPainter):
        if self.layer.isSelected:
            eyeIconPixmap = ICON_HIDDEN_HIGHLIGHT_PIXMAP if self.layer.isHidden else ICON_VISIBLE_HIGHLIGHT_PIXMAP
        else:
            eyeIconPixmap = ICON_HIDDEN_PIXMAP if self.layer.isHidden else ICON_VISIBLE_PIXMAP

        painter.drawPixmap(self.eyeIconRect(), eyeIconPixmap)

    def drawThumbnail(self, painter: QPainter):
        layerSize = self.layer.size()

        if layerSize.width() == 0:
            return

        thumbnailRect = self.thumbnailRect()
        scaledSize = layerSize.scaled(THUMBNAIL_SIZE, Qt.AspectRatioMode.KeepAspectRatio)
        painter.save()
        painter.translate(
            thumbnailRect.center().x() - scaledSize.width() / 2,
            thumbnailRect.center().y() - scaledSize.height() / 2,
        )
        scale = scaledSize.width() / layerSize.width()
        painter.scale(scale, scale)
        self.layer.draw(painter)
        painter.restore()

    def drawName(self, painter: QPainter):
        painter.save()
        if self.layer.isSelected:
            painter.setPen(self.palette.highlightedText().color())
        painter.drawText(self.layerNameRect(), Qt.AlignmentFlag.AlignVCenter, self.layer.name)
        painter.restore()

    def draw(self, painter: QPainter):
        self.drawBackground(painter)
        self.drawEyeIcon(painter)
        self.drawThumbnail(painter)
        self.drawName(painter)


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

    def iterItems(self):
        x = 0
        y = -1 * self._scrollPos
        # TODO: recursively return items (when layer groups or child layers are implemented)
        for layer in self.project.iterLayersFrontToBack():
            item = TreeViewItem(x, y, layer, self.width(), THUMBNAIL_SIZE.height(), self.palette())
            yield item
            y += item.height

    def iterVisibleItems(self):
        for item in self.iterItems():
            if (item.y + item.height) < 0:
                continue
            elif item.y > self.height():
                break
            else:
                yield item

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
        return sum(item.height for item in self.iterItems())

    def calcMaxScrollPos(self):
        """Calculate the scroll position needed to make the very bottom item visible without excess,
        if the widget height is already enough to display all items it returns 0 (no need to scroll)"""
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
            scrollDelta = (angleDelta.y() // 15) * 4

        if self.height() < self.calcItemsScreenHeight():
            # Only scroll if height is not enough to display all items
            self.updateScrollPos(scrollDelta)

        event.accept()

    def findItemUnderPosition(self, pos: QPoint):
        for item in self.iterItems():
            if item.containsYPos(pos.y()):
                return item
        return None

    def mousePressEvent(self, event: QMouseEvent) -> None:
        itemUnderMouse = self.findItemUnderPosition(event.pos())
        if itemUnderMouse is None:
            return

        layer = itemUnderMouse.layer

        if itemUnderMouse.eyeIconRect().contains(event.pos()):
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
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        painter.fillRect(event.rect(), self.palette().base())
        for item in self.iterVisibleItems():
            item.draw(painter)
        painter.end()
