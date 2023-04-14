from PyQt6.QtCore import QSize
from PyQt6.QtGui import QActionGroup, QAction
from PyQt6.QtWidgets import QWidget

from awesome_image_editor.toolbar import ToolBar


class ToolsToolbar(ToolBar):
    def __init__(self, parent: QWidget):
        super().__init__("Tools", parent)

        self.setIconSize(QSize(24, 24))
        ICON_MOVE = self.getTintedIcon("tools/tool_move.svg")
        ICON_CROP = self.getTintedIcon("tools/tool_crop.svg")

        toolsActionGroup = QActionGroup(self)
        toolsActionGroup.setExclusive(True)

        # TODO: move tool functionality
        moveAction = QAction(ICON_MOVE, "Move", self)
        moveAction.setCheckable(True)
        moveAction.setChecked(True)
        toolsActionGroup.addAction(moveAction)
        self.addAction(moveAction)

        cropAction = QAction(ICON_CROP, "Crop", self)
        cropAction.setCheckable(True)
        toolsActionGroup.addAction(cropAction)
        self.addAction(cropAction)
