from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy, QSpacerItem
from PyQt6.QtCore import Qt

from awesome_image_editor.tree_view import LayersTreeView


class LayersWidget(QWidget):
    def __init__(self, tree_view: LayersTreeView):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        label = QLabel("Layers")
        layout.addWidget(label, stretch=0, alignment=Qt.AlignmentFlag.AlignTop)
        layout.addWidget(tree_view, stretch=1)
