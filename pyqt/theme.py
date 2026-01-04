### theme.py ###
"""Theme and styling for the application."""
from __future__ import annotations

from PyQt6.QtGui import QColor, QFont, QPalette
from PyQt6.QtWidgets import QApplication


def apply_theme(app: QApplication) -> None:
    """Apply modern dark theme."""
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 9))

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(16, 17, 20))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(236, 237, 240))
    palette.setColor(QPalette.ColorRole.Base, QColor(18, 19, 23))
    palette.setColor(QPalette.ColorRole.Text, QColor(236, 237, 240))
    palette.setColor(QPalette.ColorRole.Button, QColor(24, 25, 29))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(236, 237, 240))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(92, 140, 255))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)

    app.setStyleSheet("""
        #Root {
            background: #101114;
        }
        QLabel {
            color: #eceef0;
        }
        QLabel#DimText {
            color: #9aa0a6;
            font-size: 12px;
        }
        QLabel#AppTitle {
            font-size: 16px;
            font-weight: 700;
        }
        QLabel#CardTitle {
            font-size: 11px;
            font-weight: 700;
            color: #d7dbe0;
            text-transform: uppercase;
        }
        QFrame#Card {
            background: #121317;
            border: 1px solid #22242b;
            border-radius: 6px;
        }
        QTextEdit {
            background: #0f1013;
            border: 1px solid #262933;
            border-radius: 6px;
            padding: 10px;
            color: #eceef0;
            selection-background-color: #5c8cff;
        }
        QPlainTextEdit#LogView {
            background: #0f1013;
            border: 1px solid #262933;
            border-radius: 6px;
            padding: 8px;
            color: #d6dae0;
            font-family: Consolas, monospace;
            font-size: 12px;
        }
        QComboBox {
            background: #0f1013;
            border: 1px solid #262933;
            border-radius: 5px;
            padding: 6px 8px;
            color: #eceef0;
        }
        QComboBox:hover {
            border-color: #363b47;
        }
        QComboBox::drop-down {
            border: none;
        }
        QComboBox QAbstractItemView {
            background: #121317;
            border: 1px solid #262933;
            selection-background-color: #5c8cff;
        }
        QPushButton {
            background: #171922;
            border: 1px solid #2b3040;
            border-radius: 5px;
            padding: 6px 10px;
            font-weight: 600;
            color: #eceef0;
        }
        QPushButton:hover {
            background: #1b1e29;
            border-color: #363b47;
        }
        QPushButton:pressed {
            background: #141620;
        }
        QPushButton:disabled {
            background: #0f1013;
            color: #5a5f6a;
            border-color: #1a1c22;
        }
        QToolButton {
            background: #171922;
            border: 1px solid #2b3040;
            border-radius: 5px;
            padding: 5px 8px;
            font-weight: 700;
            color: #eceef0;
        }
        QToolButton:hover {
            background: #1b1e29;
            border-color: #363b47;
        }
        QSlider::groove:horizontal {
            height: 5px;
            border-radius: 2px;
            background: #262933;
        }
        QSlider::handle:horizontal {
            width: 12px;
            margin: -5px 0;
            border-radius: 6px;
            background: #5c8cff;
        }
        QCheckBox {
            spacing: 6px;
            color: #eceef0;
        }
        QCheckBox::indicator {
            width: 11px;
            height: 11px;
            border: 2px solid #262933;
            border-radius: 3px;
            background: #0f1013;
        }
        QCheckBox::indicator:checked {
            background: #5c8cff;
            border-color: #5c8cff;
        }
        QSplitter::handle {
            background: transparent;
        }
    """)
