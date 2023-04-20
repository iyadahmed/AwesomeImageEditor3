from abc import ABC, abstractmethod

from PyQt6.QtGui import QTransform, QMouseEvent, QKeyEvent, QIcon

from awesome_image_editor.project_model import ProjectModel


class CanvasToolABC(ABC):
    @abstractmethod
    def mousePress(self, event: QMouseEvent, canvasTransform: QTransform, project: ProjectModel): ...

    @abstractmethod
    def mouseMove(self, event: QMouseEvent, canvasTransform: QTransform, project: ProjectModel): ...

    @abstractmethod
    def mouseRelease(self, event: QMouseEvent, canvasTransform: QTransform, project: ProjectModel): ...

    @abstractmethod
    def keyPress(self, event: QKeyEvent): ...

    @abstractmethod
    def keyRelease(self, event: QKeyEvent): ...

    @property
    @abstractmethod
    def icon(self) -> QIcon: ...

    @property
    @abstractmethod
    def title(self) -> str: ...
