from pathlib import Path

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy, QSpacerItem, QHBoxLayout
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon

from awesome_image_editor.tree_view import LayersTreeView

ICON_LAYERS = QIcon((Path(__file__).parent / "icons/layers/layers_dialog.svg").as_posix())


class LayersWidget(QWidget):
    def __init__(self, tree_view: LayersTreeView):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        titleLayout = QHBoxLayout()
        titleLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        titleIconLabel = QLabel()
        titleIconLabel.setPixmap(ICON_LAYERS.pixmap(QSize(24, 24)))
        titleLayout.addWidget(titleIconLabel)
        titleLabel = QLabel("Layers")
        titleLayout.addWidget(titleLabel)

        layout.addLayout(titleLayout)
        # layout.addWidget(label, stretch=0, alignment=Qt.AlignmentFlag.AlignTop)
        layout.addWidget(tree_view, stretch=1)
