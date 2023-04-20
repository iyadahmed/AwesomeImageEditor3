from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QToolBar, QWidget, QProxyStyle, QStyle, QStyleOption

from awesome_image_editor.icons import getIcon, getFullIconPath

ICON_TOOLBAR_EXTENSION_HORIZONTAL_RTL = getIcon("toolbar/extension_horizontal_rtl.svg")
ICON_TOOLBAR_EXTENSION_HORIZONTAL = getIcon("toolbar/extension_horizontal.svg")
ICON_TOOLBAR_EXTENSION_VERTICAL = getIcon("toolbar/extension_vertical.svg")


class ToolBarStyle(QProxyStyle):
    def standardIcon(self, standardIcon: QStyle.StandardPixmap, option: Optional[QStyleOption] = ...,
                     widget: Optional[QWidget] = ...) -> QIcon:
        # Changing QToolBar extension button icon
        # based on: https://forum.qt.io/post/622513
        if standardIcon == QStyle.StandardPixmap.SP_ToolBarHorizontalExtensionButton:
            if option.direction == Qt.LayoutDirection.RightToLeft:
                return ICON_TOOLBAR_EXTENSION_HORIZONTAL_RTL
            else:
                return ICON_TOOLBAR_EXTENSION_HORIZONTAL

        elif standardIcon == QStyle.StandardPixmap.SP_ToolBarVerticalExtensionButton:
            return ICON_TOOLBAR_EXTENSION_VERTICAL

        return super().standardIcon(standardIcon, option, widget)


class ToolBar(QToolBar):
    def __init__(self, title: str, parent: Optional[QWidget]):
        super().__init__(title, parent)

        self.setStyle(ToolBarStyle(self.style()))

        self.setStyleSheet(
            f"QToolBar::handle::vertical {{image: url({getFullIconPath('toolbar/handle_vertical.svg')});}}"
            f"QToolBar::handle::horizontal {{image: url({getFullIconPath('toolbar/handle_horizontal.svg')})}}"
            "QToolBar {border: 0px;}"
            "QToolButton {border: none; border-radius: 3px; padding: 3px}"
            "QToolButton::hover {background: palette(base);}"
            "QToolButton::on {background: palette(base);}"

            # Styling QToolBar extension button
            # https://stackoverflow.com/a/30718289/8094047
            # https://bugreports.qt.io/browse/QTBUG-64527?attachmentSortBy=dateTime
            "QToolBarExtension {padding: 0px;}"
        )
