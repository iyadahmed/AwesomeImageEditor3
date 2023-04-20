from typing import Optional

from PyQt6.QtCore import QSize, QPoint, QEvent, QMargins, QRect, Qt
from PyQt6.QtGui import QPainter, QPaintEvent, QMouseEvent
from PyQt6.QtWidgets import QWidget

from awesome_image_editor.canvas_tools.tools.crop import CropTool
from awesome_image_editor.canvas_tools.tools.move import MoveTool
from awesome_image_editor.pixmap_utils import getTintedPixmap

PADDING = 3
SPACING = 3


class CanvasToolBar(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self._iconSize = QSize(24, 24)
        self._buttonSize = self._iconSize.grownBy(QMargins(PADDING, PADDING, PADDING, PADDING))

        self.setFixedWidth(self._buttonSize.width())

        self._currentTool = MoveTool()
        self._tools = [
            self._currentTool,
            CropTool(),
        ]

        # Enable mouse tracking to generate mouse move events without needing to press mouse buttons,
        # so we can implement mouse hover behavior
        self.setMouseTracking(True)

        self._currentMousePos: Optional[QPoint] = None

    def getCurrentTool(self):
        return self._currentTool

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        self._currentMousePos = event.pos()
        self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        for buttonRect, tool in self.iterButtons():
            if buttonRect.contains(event.pos()):
                if not (self._currentTool is tool):
                    self._currentTool = tool
                    self.update()
                break

    def leaveEvent(self, event: QEvent) -> None:
        self._currentMousePos = None
        self.update()
        super().leaveEvent(event)

    def drawButtonBackground(self, painter: QPainter, rect: QRect):
        painter.save()
        painter.setBrush(self.palette().base())
        painter.setPen(Qt.PenStyle.NoPen)  # https://stackoverflow.com/a/28967494/8094047
        painter.drawRoundedRect(rect, 3, 3)
        painter.restore()

    def iterButtons(self):
        y = 0
        for tool in self._tools:
            yield QRect(QPoint(0, y), self._buttonSize), tool
            y += self._buttonSize.height() + SPACING

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter()
        painter.begin(self)

        for buttonRect, tool in self.iterButtons():
            if self._currentMousePos is not None:
                if buttonRect.contains(self._currentMousePos):
                    self.drawButtonBackground(painter, buttonRect)

            # TODO: cache icons
            iconPixmap = tool.icon.pixmap(self._iconSize)
            if tool is self._currentTool:
                iconPixmap = getTintedPixmap(iconPixmap, self.palette().highlightedText())
                self.drawButtonBackground(painter, buttonRect)

            painter.drawPixmap(buttonRect.x() + self._buttonSize.width() // 2 - self._iconSize.width() // 2,
                               buttonRect.y() + self._buttonSize.height() // 2 - self._iconSize.height() // 2,
                               iconPixmap)

        painter.end()
