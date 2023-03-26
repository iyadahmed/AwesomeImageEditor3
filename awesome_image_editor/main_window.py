import os
from pathlib import Path

from PyQt6.QtCore import QStandardPaths, Qt
from PyQt6.QtGui import QImage
from PyQt6.QtWidgets import QDockWidget, QFileDialog, QMainWindow, QMessageBox

from awesome_image_editor.canvas_view import LayersCanvasView
from awesome_image_editor.layers import ImageLayer, Layer
from awesome_image_editor.tree_view import LayersTreeView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setStyleSheet(r"""
            QMainWindow::separator {background: palette(window);}
            QMainWindow::separator:hover {background: palette(highlight)}
        """)

        self.layers: list[Layer] = []

        self.canvasWidget = LayersCanvasView(self.layers)
        self.setCentralWidget(self.canvasWidget)

        leftDock = QDockWidget("Layers", self)
        leftDock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        self.treeWidget = LayersTreeView(self.layers)
        leftDock.setWidget(self.treeWidget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, leftDock)
        self.resizeDocks([leftDock], [self.size().width() // 2], Qt.Orientation.Horizontal)

        def onVisibilityChange():
            self.canvasWidget.repaintCache()
            self.canvasWidget.update()

        self.treeWidget.layerVisibilityChanged.connect(onVisibilityChange)

        self.createMenus()

    def importImages(self):
        pictureLocations = QStandardPaths.standardLocations(QStandardPaths.StandardLocation.PicturesLocation)
        if len(pictureLocations) == 0:
            directory = os.path.expanduser("~")
        else:
            directory = pictureLocations[0]

        fileNames, selectedFilter = QFileDialog.getOpenFileNames(
            self, "Import Image/s", directory, "Image Files (*.jpg *.png *.jpeg)"
        )
        failedFileNames = []
        for fileName in fileNames:
            image = QImage(fileName)
            if image.isNull():
                failedFileNames.append(fileName)
                continue
            layer = ImageLayer(image)
            layer.name = Path(fileName).stem
            self.layers.append(layer)

        self.treeWidget.update()
        self.canvasWidget.repaintCache()
        self.canvasWidget.update()
        self.canvasWidget.fitView()

        if len(failedFileNames) > 0:
            QMessageBox.warning(
                self,
                "Failed to load images",
                "Some images failed to load:\n" + "\n".join(failedFileNames),
            )

    def createMenus(self):
        fileMenu = self.menuBar().addMenu("&File")
        fileMenu.addAction("Import Image/s", self.importImages)
