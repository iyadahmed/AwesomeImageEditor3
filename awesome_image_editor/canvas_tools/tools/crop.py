from PyQt6.QtGui import QMouseEvent, QTransform, QKeyEvent

from awesome_image_editor.canvas_tools.canvas_tool_abc import CanvasToolABC
from awesome_image_editor.icons import getIcon
from awesome_image_editor.project_model import ProjectModel


class CropTool(CanvasToolABC):
    icon = getIcon("tools/tool_crop.svg")
    title = "Crop"

    def mouseRelease(self, event: QMouseEvent, canvasTransform: QTransform, project: ProjectModel):
        pass

    def keyPress(self, event: QKeyEvent):
        pass

    def keyRelease(self, event: QKeyEvent):
        pass

    def mousePress(self, event: QMouseEvent, canvasTransform: QTransform, project: ProjectModel):
        pass

    def mouseMove(self, event: QMouseEvent, canvasTransform: QTransform, project: ProjectModel):
        pass
