from typing import Optional

from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QMouseEvent, QTransform, QKeyEvent

from awesome_image_editor.icons import getIcon
from awesome_image_editor.project_model import ProjectModel
from awesome_image_editor.canvas_tools.canvas_tool_abc import CanvasToolABC


class MoveTool(CanvasToolABC):
    icon = getIcon("tools/tool_move.svg")
    title = "Move"

    def __init__(self):
        self._lastMousePos: Optional[QPoint] = None

    def mousePress(self, event: QMouseEvent, canvasTransform: QTransform, project: ProjectModel):
        if event.buttons() & Qt.MouseButton.LeftButton:
            canvasInverseTransform = canvasTransform.inverted()[0]
            self._lastMousePos = canvasInverseTransform.map(event.pos())

    def mouseMove(self, event: QMouseEvent, canvasTransform: QTransform, project: ProjectModel):
        if self._lastMousePos is not None:
            canvasInverseTransform = canvasTransform.inverted()[0]
            currentMousePos = canvasInverseTransform.map(event.pos())
            delta = currentMousePos - self._lastMousePos
            self._lastMousePos = currentMousePos

            for layer in project.iterLayersBackToFront():
                if layer.isSelected:
                    layer.location += delta

            project.layersVisibilityChanged.emit()

    def mouseRelease(self, event: QMouseEvent, canvasTransform: QTransform, project: ProjectModel):
        ...

    def keyPress(self, event: QKeyEvent):
        ...

    def keyRelease(self, event: QKeyEvent):
        ...
