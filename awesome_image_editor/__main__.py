import sys

from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication

from awesome_image_editor.main_window import MainWindow

app = QApplication(sys.argv)

app.setOrganizationName("SideProject")
app.setOrganizationDomain("side-project.com")
app.setApplicationName("Awesome Image Editor")

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

mainWindow = MainWindow()
mainWindow.showMaximized()
app.exec()
