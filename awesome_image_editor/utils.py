from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QTransform


def calcTransformFitSize1ToSize2(size1: QSize, size2: QSize):
    scaled_size = size1.scaled(size2, Qt.AspectRatioMode.KeepAspectRatio)
    scale = scaled_size.width() / size1.width()

    transform = QTransform()
    transform.translate(size2.width() / 2 - scaled_size.width() / 2, size2.height() / 2 - scaled_size.height() / 2)
    transform.scale(scale, scale)

    return transform
