from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QToolBar, QVBoxLayout, QWidget

from awesome_image_editor.icons import getFullIconPath, getIcon
from awesome_image_editor.project_model import ProjectModel
from awesome_image_editor.tree_view import TreeView

ICON_LAYERS = getIcon("layers/layers_dialog.svg")
ICON_DELETE = getIcon("layers/delete_btn.svg")
ICON_LOWER = getIcon("layers/lower_layer_onestep.svg")
ICON_RAISE = getIcon("layers/raise_layer_onestep.svg")


class LayersToolbar(QToolBar):
    def __init__(self, project: ProjectModel):
        super().__init__()
        self._project = project

        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.addAction(ICON_LOWER, "Lower", self.onIconLowerPress)
        self.addAction(ICON_RAISE, "Raise", self.onIconRaisePress)
        self.addAction(ICON_DELETE, "Delete", self.onIconDeletePress)

        # Styling QToolBar extension button
        # https://stackoverflow.com/a/30718289/8094047
        # https://bugreports.qt.io/browse/QTBUG-64527?attachmentSortBy=dateTime
        self.setStyleSheet(
            "QToolBarExtension {"
            f"qproperty-icon: url({getFullIconPath('layers/unspread_left.svg')});"
            "}"
        )

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
        titleIconLabel.setPixmap(ICON_LAYERS.pixmap(QSize(24, 24)))
        titleLayout.addWidget(titleIconLabel)
        titleLabel = QLabel("Layers")
        titleLayout.addWidget(titleLabel)

        layout.addLayout(titleLayout)
        layout.addWidget(TreeView(project), stretch=1)
        layout.addWidget(LayersToolbar(project))
