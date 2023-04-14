from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from awesome_image_editor.icons import getIcon
from awesome_image_editor.project_model import ProjectModel
from awesome_image_editor.toolbar import ToolBar
from awesome_image_editor.tree_view import TreeView


class LayerOperationsToolBar(ToolBar):
    def __init__(self, project: ProjectModel):
        super().__init__("Layer Operations", None)
        self._project = project

        self.setIconSize(QSize(24, 24))
        ICON_DELETE = self.getTintedIcon("layers/delete_btn.svg")
        ICON_LOWER = self.getTintedIcon("layers/lower_layer_onestep.svg")
        ICON_RAISE = self.getTintedIcon("layers/raise_layer_onestep.svg")

        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.addAction(ICON_LOWER, "Lower", self.onIconLowerPress)
        self.addAction(ICON_RAISE, "Raise", self.onIconRaisePress)
        self.addAction(ICON_DELETE, "Delete", self.onIconDeletePress)

    def onIconDeletePress(self):
        self._project.deleteSelected()
        self._project.layersDeleted.emit()

    def onIconRaisePress(self):
        self._project.raiseSelectedLayers()
        self._project.layersOrderChanged.emit()

    def onIconLowerPress(self):
        self._project.lowerSelectedLayers()
        self._project.layersOrderChanged.emit()


class LayersWidget(QWidget):
    def __init__(self, project: ProjectModel):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        titleLayout = QHBoxLayout()
        titleLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        titleIconLabel = QLabel()
        titleIconLabel.setPixmap(getIcon("layers/layers_dialog.svg").pixmap(QSize(24, 24)))
        titleLayout.addWidget(titleIconLabel)
        titleLabel = QLabel("Layers")
        titleLayout.addWidget(titleLabel)

        layout.addLayout(titleLayout)
        layout.addWidget(TreeView(project), stretch=1)
        layout.addWidget(LayerOperationsToolBar(project))
