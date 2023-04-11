from PyQt6.QtCore import QSize

from awesome_image_editor.layers import Layer


class Project:
    def __init__(self, canvasSize: QSize):
        self._layers: list[Layer] = []
        self._canvasSize = canvasSize

    @property
    def layers(self):
        return self._layers

    @property
    def canvasSize(self):
        return self._canvasSize
