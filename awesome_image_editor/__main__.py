import sys

from awesome_image_editor.app import Application

# Create app before importing main window to ensure a QApplication is created before any pixmaps,
# and before accessing palette through QApplication for example
app = Application(sys.argv)

from awesome_image_editor.main_window import MainWindow  # noqa

mainWindow = MainWindow()
mainWindow.showMaximized()
app.exec()
