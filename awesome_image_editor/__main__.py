import sys

from PyQt6.QtWidgets import QApplication

from awesome_image_editor.main_window import MainWindow

app = QApplication(sys.argv)

app.setOrganizationName("SideProject")
app.setOrganizationDomain("side-project.com")
app.setApplicationName("Awesome Image Editor")

mainWindow = MainWindow()
mainWindow.showMaximized()
app.exec()
