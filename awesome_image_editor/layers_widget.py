from pathlib import Path

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget, QToolBar

from awesome_image_editor.tree_view import LayersTreeView

ICON_LAYERS = QIcon((Path(__file__).parent / "icons/layers/layers_dialog.svg").as_posix())
ICON_DELETE = QIcon((Path(__file__).parent / "icons/layers/delete_btn.svg").as_posix())


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
        layout.addWidget(tree_view, stretch=1)

        toolbar = QToolBar()
        toolbar.addAction(ICON_DELETE, "Delete", tree_view.deleteSelected)
        layout.addWidget(toolbar)
