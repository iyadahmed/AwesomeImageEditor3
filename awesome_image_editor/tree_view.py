from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QPoint, QPointF, QRect, QRectF, QSize, Qt, pyqtSignal
from PyQt6.QtGui import QBrush, QMouseEvent, QPainter, QPaintEvent, QPixmap
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import QApplication, QWidget

from awesome_image_editor.layers import Layer

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


class LayersTreeView(QWidget):
    layerVisibilityChanged = pyqtSignal()
    layerSelectionChanged = pyqtSignal()

    def __init__(self, layers: list[Layer]):
        super().__init__()
        self.layers = layers

    def deselectAll(self):
        for layer in self.layers:
            layer.isSelected = False

    def findItemUnderPosition(self, pos: QPoint):
        y = 0
        x = 0
        for layer in self.layers[::-1]:
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
            self.layerVisibilityChanged.emit()
        else:
            if event.buttons() & Qt.MouseButton.LeftButton:
                self.deselectAll()
                layer.isSelected = True

        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter()
        painter.begin(self)

        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        painter.fillRect(event.rect(), self.palette().window())
        painter.save()

        x = 0
        y = 0

        for layer in self.layers[::-1]:
            treeItemRect = QRect(0, y, self.size().width(), THUMBNAIL_SIZE.height())

            if layer.isSelected:
                painter.fillRect(treeItemRect, self.palette().highlight())

            eyeIconRect = QRect(
                MARGIN,
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
                    MARGIN + EYE_ICON_WIDTH + MARGIN,
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
                MARGIN + EYE_ICON_WIDTH + MARGIN + THUMBNAIL_SIZE.width() + MARGIN,
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
