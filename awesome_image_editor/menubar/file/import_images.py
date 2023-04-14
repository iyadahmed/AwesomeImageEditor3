import os
from pathlib import Path

from PyQt6.QtCore import QStandardPaths, Qt, QTimer
from PyQt6.QtGui import QImage
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QProgressDialog, QWidget

from awesome_image_editor.layers import ImageLayer
from awesome_image_editor.project_model import ProjectModel


def importImages(parent: QWidget, project: ProjectModel):
    pictureLocations = QStandardPaths.standardLocations(QStandardPaths.StandardLocation.PicturesLocation)
    if len(pictureLocations) == 0:
        directory = os.path.expanduser("~")
    else:
        directory = pictureLocations[0]

    fileNames, selectedFilter = QFileDialog.getOpenFileNames(
        parent, "Import Image/s", directory, "Image Files (*.jpg *.png *.jpeg)"
    )
    if len(fileNames) == 0:
        return

    # Import images in a non-blocking fashion using a timer and a progress bar dialog
    failedFileNames = []
    importedLayers = []
    timer = QTimer(parent)
    progress = 0
    fileNamesIter = iter(fileNames)
    progressDialog = QProgressDialog("Loading images...", None, 0, len(fileNames), parent)

    # Disable window exit button https://forum.qt.io/post/423015
    progressDialog.setWindowFlags(
        Qt.WindowType.Window | Qt.WindowType.WindowTitleHint | Qt.WindowType.CustomizeWindowHint
    )

    progressDialog.show()
    progressDialog.setWindowModality(Qt.WindowModality.NonModal)

    def finish():
        timer.stop()
        progressDialog.setValue(len(fileNames))
        project.addLayersToFront(importedLayers)
        project.layersAdded.emit()
        if len(failedFileNames) > 0:
            QMessageBox.warning(
                parent,
                "Failed to load images",
                "Some images failed to load:\n" + "\n".join(failedFileNames),
            )

    def importSingleImage():
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
        importedLayers.append(layer)

    # progressDialog.canceled.connect(finish)  # In case we want to make it cancellable later
    timer.timeout.connect(importSingleImage)
    timer.start(0)
