from pathlib import Path

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMainWindow, QSplitter, QToolBar

from awesome_image_editor.canvas_view import CanvasView
from awesome_image_editor.layers_widget import LayersWidget
from awesome_image_editor.menubar.file.import_images import importImages
from awesome_image_editor.project_model import ProjectModel

ICON_MOVE = QIcon((Path(__file__).parent / "icons/tools/tool_move.svg").as_posix())
FILEPATH_ICON_HANDLE_VERTICAL = (Path(__file__).parent / 'icons/tools/handle_vertical.svg').as_posix()
FILEPATH_ICON_HANDLE_HORIZONTAL = (Path(__file__).parent / 'icons/tools/handle_horizontal.svg').as_posix()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.project = ProjectModel(QSize(1920, 1080))

        splitter = QSplitter()
        self.setStyleSheet(
            "QSplitter::handle {background: palette(window);}"
            "QSplitter::handle:hover {background: palette(highlight);}"
        )
        self.setCentralWidget(splitter)

        canvasWidget = CanvasView(self.project)
        layersWidget = LayersWidget(self.project)
        splitter.addWidget(canvasWidget)
        splitter.addWidget(layersWidget)
        splitter.setSizes([self.width() - self.width() // 5, self.width() // 5])

        toolsToolBar = QToolBar("Tools")
        toolsToolBar.setStyleSheet(
            f"QToolBar::handle::vertical {{image: url({FILEPATH_ICON_HANDLE_VERTICAL});}}"
            f"QToolBar::handle::horizontal {{image: url({FILEPATH_ICON_HANDLE_HORIZONTAL})}}"
        )
        # TODO: move tool functionality
        toolsToolBar.addAction(ICON_MOVE, "Move", lambda: ...)
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, toolsToolBar)

        self.createMenus()

    def createMenus(self):
        fileMenu = self.menuBar().addMenu("&File")
        fileMenu.addAction("Import Image/s", lambda: importImages(self, self.project))
