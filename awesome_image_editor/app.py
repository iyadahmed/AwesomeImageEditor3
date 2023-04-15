import platform
from pathlib import Path

from PyQt6.QtGui import QFontDatabase
from PyQt6.QtWidgets import QApplication

from awesome_image_editor.icons import getIcon
from awesome_image_editor.palette import AIE_PALETTE


class Application(QApplication):
    def __init__(self, argv: list[str]):
        super().__init__(argv)

        # Load and set fonts
        for entry in (Path(__file__).parent / "fonts/cantarell").iterdir():
            QFontDatabase.addApplicationFont(entry.as_posix())
        self.setStyleSheet('QWidget {font-family: "Cantarell Regular";}')

        # Set meta data
        self.setOrganizationName("AwesomeImageEditor")
        self.setOrganizationDomain("AwesomeImageEditor.org")
        self.setApplicationName("Awesome Image Editor")

        # Fixes app icon not displayed in Windows taskbar
        if platform.system() == "Windows":
            import ctypes
            appID = "AwesomeImageEditor.AwesomeImageEditor.AwesomeImageEditor.3"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appID)  # noqa

        # Set application icon
        self.setWindowIcon(getIcon("app2.svg"))

        # Set style and palette
        self.setStyle("Fusion")
        self.setPalette(AIE_PALETTE)
