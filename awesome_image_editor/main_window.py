from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QMainWindow, QSplitter

from awesome_image_editor.canvas_view import CanvasView
from awesome_image_editor.layers_widget import LayersWidget
from awesome_image_editor.project_model import ProjectModel
from awesome_image_editor.menubar.file.import_images import importImages


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

        self.createMenus()

    def createMenus(self):
        fileMenu = self.menuBar().addMenu("&File")
        fileMenu.addAction("Import Image/s", lambda: importImages(self, self.project))
