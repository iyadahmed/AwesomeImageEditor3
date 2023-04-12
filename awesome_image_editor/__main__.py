import ctypes
import platform
import sys
from pathlib import Path, PurePath

from PyQt6.QtGui import QColor, QFontDatabase, QIcon, QPalette
from PyQt6.QtWidgets import QApplication

app = QApplication(sys.argv)

for entry in (Path(__file__).parent / "fonts/cantarell").iterdir():
    fontID = QFontDatabase.addApplicationFont(entry.as_posix())

app.setStyleSheet('QWidget {font-family: "Cantarell Regular";}')

app.setOrganizationName("AwesomeImageEditor")
app.setOrganizationDomain("AwesomeImageEditor.org")
app.setApplicationName("Awesome Image Editor")

# Fixes app icon not displayed in Windows taskbar
if platform.system() == "Windows":
    appID = "AwesomeImageEditor.AwesomeImageEditor"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appID)  # noqa

app.setWindowIcon(QIcon((PurePath(__file__).parent / "icons" / "app2.svg").as_posix()))

# Dark theme + modifications by @alezzacreative (Twitter, GitHub)
# https://stackoverflow.com/a/56851493/8094047
app.setStyle("Fusion")
palette = QPalette()
palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
palette.setColor(QPalette.ColorRole.WindowText, QColor(175, 175, 175))
palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(167, 0, 72))
palette.setColor(QPalette.ColorRole.ToolTipText, QColor(175, 175, 175))
palette.setColor(QPalette.ColorRole.Text, QColor(175, 175, 175))
palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
palette.setColor(QPalette.ColorRole.ButtonText, QColor(175, 175, 175))
palette.setColor(QPalette.ColorRole.BrightText, QColor("white"))
palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
palette.setColor(QPalette.ColorRole.Highlight, QColor(56, 20, 35))
palette.setColor(QPalette.ColorRole.HighlightedText, QColor(167, 0, 72))
app.setPalette(palette)

# NOTE: Application is created and palette is set up before importing MainWindow to ensure QApplication is created
# before loading any Pixmap objects or accessing any palette colors

from awesome_image_editor.main_window import MainWindow  # noqa

mainWindow = MainWindow()
mainWindow.showMaximized()
app.exec()
