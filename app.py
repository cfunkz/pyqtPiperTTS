### app.py ###
from __future__ import annotations
import sys
from PyQt6.QtWidgets import QApplication
from pyqt.theme import apply_theme
from pyqt.window import MainWindow


def main() -> int:
    """Application entry point."""
    app = QApplication(sys.argv)
    apply_theme(app)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
