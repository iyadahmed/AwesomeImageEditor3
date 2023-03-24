from pathlib import Path

from PyQt6.QtCore import QPointF, QRect, QRectF, QSize, Qt, pyqtSignal
from PyQt6.QtGui import QMouseEvent, QPainter, QPaintEvent, QPixmap
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import QWidget

from awesome_image_editor.layers import Layer

THUMBNAIL_SIZE = QSize(64, 64)
EYE_ICON_WIDTH = EYE_ICON_HEIGHT = 20
MARGIN = 10


def pixmapFromSVG(filepath: Path, size: QSize):
    pixmap = QPixmap(size)
    pixmap.fill(Qt.GlobalColor.transparent)
    renderer = QSvgRenderer(filepath.as_posix())
    painter = QPainter()
    painter.begin(pixmap)
    renderer.render(painter, QRectF(QPointF(0, 0), size.toSizeF()))
    painter.end()
    return pixmap


ICON_HIDDEN_PIXMAP = pixmapFromSVG(Path(__file__).parent / "icons/layers/hidden.svg", THUMBNAIL_SIZE)
ICON_VISIBLE_PIXMAP = pixmapFromSVG(Path(__file__).parent / "icons/layers/visible.svg", THUMBNAIL_SIZE)


class LayersTreeView(QWidget):
    layerVisibilityChanged = pyqtSignal()

    def __init__(self, layers: list[Layer]):
        super().__init__()
        self.layers = layers

    def mousePressEvent(self, event: QMouseEvent) -> None:
        x = 0
        y = 0

        for layer in self.layers[::-1]:
            if y < event.pos().y() < (y + THUMBNAIL_SIZE.width()):
                eyeIconRect = QRectF(
                    MARGIN,
                    y + THUMBNAIL_SIZE.width() / 2 - EYE_ICON_WIDTH / 2,
                    EYE_ICON_WIDTH,
                    EYE_ICON_HEIGHT,
                )
                if eyeIconRect.contains(event.position()):
                    # Toggle hidden state
                    layer.isHidden = not layer.isHidden
                    self.layerVisibilityChanged.emit()

            y += THUMBNAIL_SIZE.width()

        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter()
        painter.begin(self)

        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        painter.fillRect(event.rect(), self.palette().window())
        painter.save()

        x = 0
        y = 0

        for layer in self.layers[::-1]:
            eyeIconRect = QRect(
                MARGIN,
                y + THUMBNAIL_SIZE.width() // 2 - EYE_ICON_WIDTH // 2,
                EYE_ICON_WIDTH,
                EYE_ICON_HEIGHT,
            )
            # Display hide or show icon based on hide state of layer
            painter.drawPixmap(eyeIconRect, ICON_HIDDEN_PIXMAP if layer.isHidden else ICON_VISIBLE_PIXMAP)

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

            # TODO: draw thumbnail frame over thumbnail
            # TODO: draw layer name

            y += THUMBNAIL_SIZE.width()

        painter.restore()
        painter.end()
