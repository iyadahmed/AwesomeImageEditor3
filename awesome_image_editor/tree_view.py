from abc import ABC, abstractmethod
from operator import add, sub
from pathlib import Path

from PyQt6.QtCore import QPoint, QRectF, QSize, QSizeF, Qt, pyqtSignal
from PyQt6.QtGui import QImage, QKeyEvent, QMouseEvent, QPainter, QPaintEvent, QTransform, QWheelEvent
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtSvg import QSvgRenderer

from awesome_image_editor.layers import Layer

THUMBNAIL_SIZE = QSize(64, 64)
EYE_ICON_WIDTH = EYE_ICON_HEIGHT = 16
MARGIN = 10

ICON_HIDE_RENDERER = QSvgRenderer((Path(__file__).parent / "icons/layers/hide.svg").as_posix())
ICON_SHOW_RENDERER = QSvgRenderer((Path(__file__).parent / "icons/layers/show.svg").as_posix())


class LayersTreeView(QOpenGLWidget):
    layerVisibilityChanged = pyqtSignal()

    def __init__(self, layers: list[Layer]):
        super().__init__()
        self.layers = layers

    def mousePressEvent(self, event: QMouseEvent) -> None:
        x = 0
        y = 0

        for layer in self.layers[::-1]:
            if y < event.pos().y() < (y + THUMBNAIL_SIZE.width()):
                icon_show_hide_bounds = QRectF(
                    MARGIN,
                    y + THUMBNAIL_SIZE.width() / 2 - EYE_ICON_WIDTH / 2,
                    EYE_ICON_WIDTH,
                    EYE_ICON_HEIGHT,
                )
                if icon_show_hide_bounds.contains(event.position()):
                    # Toggle hidden state
                    layer.isHidden = not layer.isHidden
                    self.layerVisibilityChanged.emit()

            y += THUMBNAIL_SIZE.width()

        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter()
        # painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        painter.begin(self)
        painter.fillRect(event.rect(), self.palette().window())
        painter.save()

        x = 0
        y = 0

        for layer in self.layers[::-1]:

            icon_show_hide_bounds = QRectF(
                MARGIN,
                y + THUMBNAIL_SIZE.width() / 2 - EYE_ICON_WIDTH / 2,
                EYE_ICON_WIDTH,
                EYE_ICON_HEIGHT,
            )
            # Display hide or show icon based on hide state of layer
            (ICON_HIDE_RENDERER if layer.isHidden else ICON_SHOW_RENDERER).render(painter, icon_show_hide_bounds)

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
