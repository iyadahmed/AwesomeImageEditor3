from pathlib import Path

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget, QToolBar

from awesome_image_editor.tree_view import TreeView

ICON_LAYERS = QIcon((Path(__file__).parent / "icons/layers/layers_dialog.svg").as_posix())
ICON_DELETE = QIcon((Path(__file__).parent / "icons/layers/delete_btn.svg").as_posix())
ICON_LOWER = QIcon((Path(__file__).parent / "icons/layers/lower_layer_onestep.svg").as_posix())
ICON_RAISE = QIcon((Path(__file__).parent / "icons/layers/raise_layer_onestep.svg").as_posix())


class LayersWidget(QWidget):
    def __init__(self, tree_view: TreeView):
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
        toolbar.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        toolbar.addAction(ICON_DELETE, "Delete", tree_view.deleteSelected)
        toolbar.addAction(ICON_RAISE, "Raise", tree_view.raiseSelectedLayers)
        toolbar.addAction(ICON_LOWER, "Lower", tree_view.lowerSelectedLayers)
        layout.addWidget(toolbar)
