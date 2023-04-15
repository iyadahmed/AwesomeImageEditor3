from PyQt6.QtGui import QPalette, QColor

# Dark theme + modifications by @alezzacreative (Twitter, GitHub)
# https://stackoverflow.com/a/56851493/8094047

AIE_PALETTE = QPalette()
"""The Awesome Image Editor palette"""

AIE_PALETTE.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
AIE_PALETTE.setColor(QPalette.ColorRole.WindowText, QColor(175, 175, 175))
AIE_PALETTE.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
AIE_PALETTE.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
AIE_PALETTE.setColor(QPalette.ColorRole.ToolTipBase, QColor(167, 0, 72))
AIE_PALETTE.setColor(QPalette.ColorRole.ToolTipText, QColor(175, 175, 175))
AIE_PALETTE.setColor(QPalette.ColorRole.Text, QColor(175, 175, 175))
AIE_PALETTE.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
AIE_PALETTE.setColor(QPalette.ColorRole.ButtonText, QColor(175, 175, 175))
AIE_PALETTE.setColor(QPalette.ColorRole.BrightText, QColor("white"))
AIE_PALETTE.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
AIE_PALETTE.setColor(QPalette.ColorRole.Highlight, QColor(56, 20, 35))
AIE_PALETTE.setColor(QPalette.ColorRole.HighlightedText, QColor(167, 0, 72))
