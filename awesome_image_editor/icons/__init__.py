from pathlib import Path

from PyQt6.QtGui import QIcon


def getFullIconPath(path: str):
    """Get an icon's full absolute path via its relative path to the "icons" directory"""
    return (Path(__file__).parent / path).as_posix()


def getIcon(path: str):
    """Get an icon via its relative path to the "icons" directory"""
    return QIcon(getFullIconPath(path))
