from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QPointF, QRect, QRectF, QSize, Qt, pyqtSignal, QPoint
from PyQt6.QtGui import QBrush, QColor, QMouseEvent, QPainter, QPaintEvent, QPixmap, QRegion
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

    def mousePressEvent(self, event: QMouseEvent) -> None:
        x = 0
        y = 0

        if event.buttons() & Qt.MouseButton.LeftButton:
            layerUnderMouse: Optional[Layer] = None
            eyeIconRect: Optional[QRectF] = None
            for layer in self.layers[::-1]:
                if y < event.pos().y() < (y + THUMBNAIL_SIZE.width()):
                    eyeIconRect = QRectF(
                        MARGIN,
                        y + THUMBNAIL_SIZE.width() / 2 - EYE_ICON_WIDTH / 2,
                        EYE_ICON_WIDTH,
                        EYE_ICON_HEIGHT,
                    )
                    layerUnderMouse = layer
                    break
                y += THUMBNAIL_SIZE.height()

            if (not (layerUnderMouse is None)) and (not (eyeIconRect is None)):
                if eyeIconRect.contains(event.position()):
                    # Toggle hidden state
                    layerUnderMouse.isHidden = not layerUnderMouse.isHidden
                    self.layerVisibilityChanged.emit()
                else:
                    for layer in self.layers:
                        if layer is layerUnderMouse:
                            if not layer.isSelected:
                                layer.isSelected = True
                                self.layerSelectionChanged.emit()
                        else:
                            layer.isSelected = False

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

            # TODO: draw thumbnail frame over thumbnail
            layerNameRect = QRect(
                MARGIN + EYE_ICON_WIDTH + MARGIN + THUMBNAIL_SIZE.width() + MARGIN,
                y,
                self.size().width(),
                THUMBNAIL_SIZE.height()
            )
            painter.drawText(layerNameRect, Qt.AlignmentFlag.AlignVCenter, layer.name)

            y += THUMBNAIL_SIZE.height()

        painter.restore()
        painter.end()
