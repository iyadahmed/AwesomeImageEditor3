from pathlib import Path

from PyQt6.QtGui import QIcon, QActionGroup, QAction
from PyQt6.QtWidgets import QWidget, QToolBar

ICON_MOVE = QIcon((Path(__file__).parent.parent / "icons/tools/tool_move.svg").as_posix())
FILEPATH_ICON_HANDLE_VERTICAL = (Path(__file__).parent.parent / 'icons/tools/handle_vertical.svg').as_posix()
FILEPATH_ICON_HANDLE_HORIZONTAL = (Path(__file__).parent.parent / 'icons/tools/handle_horizontal.svg').as_posix()


class ToolsToolbar(QToolBar):
    def __init__(self, parent: QWidget):
        super().__init__("Tools", parent)

        self.setStyleSheet(
            f"QToolBar::handle::vertical {{image: url({FILEPATH_ICON_HANDLE_VERTICAL});}}"
            f"QToolBar::handle::horizontal {{image: url({FILEPATH_ICON_HANDLE_HORIZONTAL})}}"
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
