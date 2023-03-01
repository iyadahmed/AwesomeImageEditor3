from PyQt6.QtWidgets import QMainWindow, QFileDialog
from PyQt6.QtGui import QImage

from awesome_image_editor.canvas import CanvasWidget, ImageLayer


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.canvasWidget = CanvasWidget()
        self.setCentralWidget(self.canvasWidget)

        self.createMenus()

    def importImages(self):
        fileNames, selectedFilter = QFileDialog.getOpenFileNames(
            self, "Import images", "C:\\", "Image files (*.jpg *.png *.jpeg)"
        )
        for fileName in fileNames:
            image = QImage(fileName)
            assert not image.isNull()
            self.canvasWidget.layers.append(ImageLayer(image))

    def createMenus(self):
        fileMenu = self.menuBar().addMenu("&File")
        fileMenu.addAction("Import Image", self.importImages)
