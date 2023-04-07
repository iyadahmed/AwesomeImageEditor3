import os
from pathlib import Path

from PyQt6.QtCore import QStandardPaths, Qt, QTimer
from PyQt6.QtGui import QImage
from PyQt6.QtWidgets import QDockWidget, QFileDialog, QMainWindow, QMessageBox, QProgressDialog, QSplitter

from awesome_image_editor.canvas_view import LayersCanvasView
from awesome_image_editor.layers import ImageLayer, Layer
from awesome_image_editor.tree_view import LayersTreeView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.layers: list[Layer] = []

        splitter = QSplitter()
        self.setStyleSheet(r"""
            QSplitter::handle {background: palette(window);}
            QSplitter::handle:hover {background: palette(highlight)}
        """)
        self.setCentralWidget(splitter)

        self.canvasWidget = LayersCanvasView(self.layers)
        self.treeWidget = LayersTreeView(self.layers)
        splitter.addWidget(self.canvasWidget)
        splitter.addWidget(self.treeWidget)
        splitter.setSizes([self.width() - self.width() // 5, self.width() // 5])

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
        if len(fileNames) == 0:
            return

        # Import images in a non-blocking fashion using a timer and a progress bar dialog
        failedFileNames = []
        timer = QTimer(self)
        progress = 0
        fileNamesIter = iter(fileNames)
        progressDialog = QProgressDialog("Loading images...", None, 0, len(fileNames), self)

        # Disable window exit button https://forum.qt.io/post/423015
        progressDialog.setWindowFlags(
            Qt.WindowType.Window | Qt.WindowType.WindowTitleHint | Qt.WindowType.CustomizeWindowHint)

        progressDialog.show()
        progressDialog.setWindowModality(Qt.WindowModality.NonModal)

        def finish():
            timer.stop()
            progressDialog.setValue(len(fileNames))
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

        def importImage():
            nonlocal progress
            progressDialog.setValue(progress)
            progress += 1
            fileName = next(fileNamesIter, None)
            if fileName is None:
                # No more images to load
                finish()

            progressDialog.setLabelText(f"Loading image: {fileName}")
            image = QImage(fileName)
            if image.isNull():
                failedFileNames.append(fileName)
                return  # Skip the image that failed to load

            layer = ImageLayer(image)
            layer.name = Path(fileName).stem
            self.layers.append(layer)

        # progressDialog.canceled.connect(finish)  # In case we want to make it cancellable later
        timer.timeout.connect(importImage)
        timer.start(0)

    def createMenus(self):
        fileMenu = self.menuBar().addMenu("&File")
        fileMenu.addAction("Import Image/s", self.importImages)
