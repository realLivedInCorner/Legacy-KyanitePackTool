# -*- coding: utf-8 -*-
"""
UI entrypoint (thin wrapper around refactored modules).
"""

import sys
from PySide6.QtWidgets import QApplication

from ui_components.main_window import KPTMainWindow
from ui_components.theme import apply_app_theme


def main():
    app = QApplication(sys.argv)

    apply_app_theme(app)

    window = KPTMainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
