from typing import Iterable

from PyQt6.QtCore import QObject, QSize, pyqtSignal

from awesome_image_editor.layers import Layer


class ProjectModel(QObject):
    # These signals are meant to be emitted and connected to by views and users of the model,
    # to notify other views about changes
    layersDeleted = pyqtSignal()
    layersOrderChanged = pyqtSignal()
    layersAdded = pyqtSignal()
    layersVisibilityChanged = pyqtSignal()
    layersSelectionChanged = pyqtSignal()

    def __init__(self, parent: QObject, canvasSize: QSize):
        super().__init__(parent)
        self._layers: list[Layer] = []
        self._canvasSize = canvasSize

    def addLayerToFront(self, layer: Layer):
        self._layers.append(layer)

    def addLayersToFront(self, layers: Iterable[Layer]):
        self._layers.extend(layers)

    def iterLayersBackToFront(self):
        return iter(self._layers)

    def iterLayersFrontToBack(self):
        return iter(self._layers[::-1])

    @property
    def canvasSize(self):
        return self._canvasSize

    def deleteSelected(self):
        # TODO: improve memory usage? a copy of list is made and filtered,
        #       so it uses more memory for a moment,
        #       also it is done anyway even if there are no selected layers
        #       but it is very fast, very usable and very interactive anyways for hundreds of layers.
        new_layers = [layer for layer in self._layers if not layer.isSelected]
        self._layers.clear()
        self._layers.extend(new_layers)

    def raiseSelectedLayers(self):
        for i in range(len(self._layers) - 1)[::-1]:
            if self._layers[i].isSelected and (not self._layers[i + 1].isSelected):
                self._layers[i], self._layers[i + 1] = self._layers[i + 1], self._layers[i]

    def lowerSelectedLayers(self):
        for i in range(len(self._layers) - 1):
            if self._layers[i + 1].isSelected and (not self._layers[i].isSelected):
                self._layers[i], self._layers[i + 1] = self._layers[i + 1], self._layers[i]

    def deselectAll(self):
        for layer in self._layers:
            layer.isSelected = False
