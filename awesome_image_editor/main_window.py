import os

from PyQt6.QtCore import QStandardPaths
from PyQt6.QtGui import QImage
from PyQt6.QtWidgets import QFileDialog, QMainWindow, QMessageBox

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
            self, "Import Image/s", directory, "Image Files (*.jpg *.png *.jpeg)"
        )
        failedFileNames = []
        for fileName in fileNames:
            image = QImage(fileName)
            if image.isNull():
                failedFileNames.append(fileName)
                continue
            self.canvasWidget.layers.append(ImageLayer(image))

        if len(failedFileNames) > 0:
            QMessageBox.warning(
                self,
                "Failed to load images",
                "Some images failed to load:\n" + "\n".join(failedFileNames),
            )

    def createMenus(self):
        fileMenu = self.menuBar().addMenu("&File")
        fileMenu.addAction("Import Image/s", self.importImages)
