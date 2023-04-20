from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QMainWindow, QSplitter, QWidget, QHBoxLayout

from awesome_image_editor.canvas_tools.canvas_toolbar import CanvasToolBar
from awesome_image_editor.canvas_view import CanvasView
from awesome_image_editor.layers_widget import LayersWidget
from awesome_image_editor.menubar.file.import_images import importImages
from awesome_image_editor.project_model import ProjectModel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.project = ProjectModel(self, QSize(1920, 1080))

        centralWidget = QWidget(self)
        centralWidgetLayout = QHBoxLayout()
        centralWidget.setContentsMargins(0, 0, 0, 0)
        centralWidget.setLayout(centralWidgetLayout)
        self.setCentralWidget(centralWidget)

        canvasToolBar = CanvasToolBar(self)
        centralWidgetLayout.addWidget(canvasToolBar)

        splitter = QSplitter(self)
        self.setStyleSheet(
            "QSplitter::handle {background: palette(window);}"
            "QSplitter::handle:hover {background: palette(highlight);}"
        )
        centralWidgetLayout.addWidget(splitter)

        canvasWidget = CanvasView(self, self.project, canvasToolBar)
        layersWidget = LayersWidget(self, self.project)

        splitter.addWidget(canvasWidget)
        splitter.addWidget(layersWidget)
        splitter.setSizes([self.width() - self.width() // 5, self.width() // 5])

        self.createMenus()

    def createMenus(self):
        fileMenu = self.menuBar().addMenu("&File")
        fileMenu.addAction("Import Image/s", lambda: importImages(self, self.project))
