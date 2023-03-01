import os

from PyQt6.QtCore import QStandardPaths
from PyQt6.QtGui import QImage
from PyQt6.QtWidgets import QFileDialog, QMainWindow

from awesome_image_editor.canvas import CanvasWidget, ImageLayer


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.canvasWidget = CanvasWidget()
        self.setCentralWidget(self.canvasWidget)

        self.createMenus()

    def importImages(self):
        pictureLocations = QStandardPaths.standardLocations(QStandardPaths.StandardLocation.PicturesLocation)
        if len(pictureLocations) == 0:
            directory = os.path.expanduser("~")
        else:
            directory = pictureLocations[0]

        fileNames, selectedFilter = QFileDialog.getOpenFileNames(
            self, "Import images", directory, "Image files (*.jpg *.png *.jpeg)"
        )
        for fileName in fileNames:
            image = QImage(fileName)
            assert not image.isNull()
            self.canvasWidget.layers.append(ImageLayer(image))

    def createMenus(self):
        fileMenu = self.menuBar().addMenu("&File")
        fileMenu.addAction("Import Image", self.importImages)
