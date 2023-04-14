from typing import Optional

from PyQt6.QtGui import QPixmap, QBrush, QPainter


def getTintedPixmap(pixmap: QPixmap, tint: Optional[QBrush]):
    tintedPixmap = pixmap.copy()
    painter = QPainter()
    painter.begin(tintedPixmap)
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
    painter.fillRect(tintedPixmap.rect(), tint)
    painter.end()
    return tintedPixmap
