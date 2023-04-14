from PyQt6.QtGui import QActionGroup, QAction
from PyQt6.QtWidgets import QWidget, QToolBar

from awesome_image_editor.icons import getFullIconPath, getIcon

ICON_MOVE = getIcon("tools/tool_move.svg")


class ToolsToolbar(QToolBar):
    def __init__(self, parent: QWidget):
        super().__init__("Tools", parent)

        self.setStyleSheet(
            f"QToolBar::handle::vertical {{image: url({getFullIconPath('tools/handle_vertical.svg')});}}"
            f"QToolBar::handle::horizontal {{image: url({getFullIconPath('tools/handle_horizontal.svg')})}}"
            "QToolBar {border: 0px;}"
        )
        toolsActionGroup = QActionGroup(self)
        toolsActionGroup.setExclusive(True)

        # TODO: move tool functionality
        moveAction = QAction(ICON_MOVE, "Move", self)
        moveAction.setCheckable(True)
        moveAction.setChecked(True)
        toolsActionGroup.addAction(moveAction)
        self.addAction(moveAction)
