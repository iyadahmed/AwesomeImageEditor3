from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QToolBar, QWidget, QProxyStyle, QStyle, QStyleOption

from awesome_image_editor.icons import getIcon, getFullIconPath
from awesome_image_editor.pixmap_utils import getTintedPixmap


class ToolBarStyle(QProxyStyle):
    def standardIcon(self, standardIcon: QStyle.StandardPixmap, option: Optional[QStyleOption] = ...,
                     widget: Optional[QWidget] = ...) -> QIcon:
        # Changing QToolBar extension button icon
        # based on: https://forum.qt.io/post/622513
        if standardIcon == QStyle.StandardPixmap.SP_ToolBarHorizontalExtensionButton:
            if option.direction == Qt.LayoutDirection.RightToLeft:
                return getIcon("toolbar/extension_horizontal_rtl.svg")
            else:
                return getIcon("toolbar/extension_horizontal.svg")

        elif standardIcon == QStyle.StandardPixmap.SP_ToolBarVerticalExtensionButton:
            return getIcon("toolbar/extension_vertical.svg")

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

    def getTintedIcon(self, path: str):
        """Get a QIcon with a pixmap tinted with highlighted text color for normal and active modes of "On" icon state,
        via its relative path to the "icons" directory
        """
        icon = getIcon(path)
        # TODO: it would have been better if we could override QStyle instead,
        #       but I couldn't find a way to paint over pixmap for a specific button state,
        #       I was able however to paint over it regardless of state, but not for a specific state,
        #       by subclassing QProxyStyle, passing parent style or "Fusion" to constructor
        #       and overriding drawItemPixmap.
        tintedPixmap = getTintedPixmap(icon.pixmap(self.iconSize()), self.palette().highlightedText())
        icon.addPixmap(tintedPixmap, QIcon.Mode.Normal, QIcon.State.On)
        icon.addPixmap(tintedPixmap, QIcon.Mode.Active, QIcon.State.On)
        return icon
