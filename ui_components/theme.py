# -*- coding: utf-8 -*-
"""
Theme helpers for the UI.
"""

from PySide6.QtGui import QPalette, QColor


def apply_app_theme(app):
    """Apply global palette + base style."""
    app.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(245, 245, 245))
    palette.setColor(QPalette.WindowText, QColor(10, 10, 10))
    palette.setColor(QPalette.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.AlternateBase, QColor(248, 248, 248))
    palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ToolTipText, QColor(10, 10, 10))
    palette.setColor(QPalette.Text, QColor(10, 10, 10))
    palette.setColor(QPalette.Button, QColor(255, 255, 255))
    palette.setColor(QPalette.ButtonText, QColor(10, 10, 10))
    palette.setColor(QPalette.Highlight, QColor(10, 10, 10))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)


def apply_main_window_styles(window):
    """Apply main window stylesheet."""
    style_sheet = r'''
/* Global typography */
* {
    font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
}

QMainWindow {
    background-color: #f7f7f7;
}

#contentShell {
    background-color: #f7f7f7;
}

/* Sidebar */
#sidebar {
    background-color: #ffffff;
    border-right: 1px solid #e6e6e6;
}

#brandTitle {
    color: #0a0a0a;
    font-size: 18px;
    font-weight: 700;
}

#brandSubtitle {
    color: #6b6b6b;
    font-size: 12px;
}

#navButton {
    background-color: #ffffff;
    color: #0a0a0a;
    border: 1px solid #e6e6e6;
    border-radius: 18px;
    text-align: left;
    padding: 10px 14px;
    font-size: 14px;
    font-weight: 600;
    height: 40px;
}

#navButton:hover {
    background-color: #f4f4f4;
}

#navButton:checked {
    border-color: #0a0a0a;
    border-width: 2px;
}
/* Top bar */
#topBar {
    background-color: transparent;
}

#pageTitle {
    color: #0a0a0a;
    font-size: 22px;
    font-weight: 700;
}

/* Main content */
#mainContent {
    background-color: transparent;
}

#contentScroll {
    background: transparent;
}

#contentScroll QWidget {
    background: transparent;
}
/* Hero / welcome card */
#welcomeFrame {
    background-color: #ffffff;
    border-radius: 16px;
    border: 1px solid #e6e6e6;
}

#welcomeTitle {
    color: #0a0a0a;
    font-size: 30px;
    font-weight: 700;
    margin-bottom: 8px;
    text-align: center;
}

#subtitleLabel {
    color: #222;
    font-size: 16px;
    font-weight: 500;
    line-height: 1.6;
    margin-bottom: 8px;
    max-width: 620px;
    text-align: center;
    qproperty-alignment: AlignCenter;
}

#quickActions {
    background-color: transparent;
}
/* Feature grid */
#featureGrid {
    background-color: transparent;
}

#featureCard {
    background-color: #ffffff;
    border: 1px solid #e6e6e6;
    border-radius: 14px;
}

#featureTitle {
    color: #0a0a0a;
    font-size: 16px;
    font-weight: 700;
}

#featureBody {
    color: #2a2a2a;
    font-size: 13px;
    line-height: 1.5;
}

#sectionTitle {
    color: #0a0a0a;
    font-size: 16px;
    font-weight: 700;
}

#sectionSubtitle {
    color: #666;
    font-size: 12px;
}

#fieldLabel {
    color: #111;
    font-size: 13px;
    font-weight: 600;
}
/* Buttons - 统一圆角样式 */
QPushButton {
    background-color: #f8f8f8;
    color: #0a0a0a;
    border: 1px solid #dcdcdc;
    border-radius: 18px;
    font-size: 14px;
    font-weight: 600;
    padding: 6px 16px;
    min-height: 32px;
}

QPushButton:hover {
    background-color: #f1f1f1;
    border-color: #cfcfcf;
}

QPushButton:pressed {
    background-color: #eaeaea;
    border-color: #c2c2c2;
}

#functionButton,
#startConversionButton,
#selectFileButton {
    background-color: #f8f8f8;
    color: #0a0a0a;
    border: 1px solid #dcdcdc;
    border-radius: 18px;
    font-size: 14px;
    font-weight: 600;
    padding: 6px 16px;
    min-height: 32px;
}

#functionButton:hover,
#startConversionButton:hover,
#selectFileButton:hover {
    background-color: #f1f1f1;
    border-color: #cfcfcf;
}

#functionButton:pressed,
#startConversionButton:pressed,
#selectFileButton:pressed {
    background-color: #eaeaea;
    border-color: #c2c2c2;
}

#optionButton,
#homeButton,
#selectFolderButton {
    background-color: #ffffff;
    color: #0a0a0a;
    border: 1px solid #dcdcdc;
    border-radius: 18px;
    font-size: 14px;
    font-weight: 600;
    padding: 6px 16px;
    min-height: 32px;
}

#optionButton:hover,
#homeButton:hover,
#selectFolderButton:hover {
    background-color: #f1f1f1;
    border-color: #cfcfcf;
}

#optionButton:pressed,
#homeButton:pressed,
#selectFolderButton:pressed {
    background-color: #eaeaea;
    border-color: #c2c2c2;
}

/* Menu bar */
QMenuBar {
    background-color: #ffffff;
    border-bottom: 1px solid #e6e6e6;
}

QMenuBar::item {
    padding: 8px 12px;
    background-color: transparent;
}

QMenuBar::item:selected {
    background-color: #f2f2f2;
}

QMenu {
    background-color: #ffffff;
    border: 1px solid #e6e6e6;
}

QMenu::item {
    padding: 8px 20px;
}

QMenu::item:selected {
    background-color: #f2f2f2;
}

/* Inputs */
QLineEdit,
QTextEdit,
QComboBox {
    border: 1px solid #d9d9d9;
    border-radius: 10px;
    padding: 8px 12px;
    background-color: #ffffff;
    font-size: 14px;
    color: #0a0a0a;
}

QLineEdit:focus,
QTextEdit:focus,
QComboBox:focus {
    border-color: #0a0a0a;
    background-color: #ffffff;
}

QComboBox QAbstractItemView {
    border: 1px solid #d9d9d9;
    border-radius: 10px;
    background-color: #ffffff;
    selection-background-color: #0a0a0a;
    selection-color: #ffffff;
    color: #0a0a0a;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox::down-arrow {
    image: none;
    border: 2px solid #0a0a0a;
    border-top: none;
    border-right: none;
    width: 6px;
    height: 6px;
    margin-right: 10px;
}

/* Drag drop card */
#dragDropFrame {
    background-color: #ffffff;
    border: 1px dashed #cfcfcf;
    border-radius: 14px;
}

#dragDropLabel {
    color: #444;
    font-size: 14px;
}

/* Progress bar */
QProgressBar {
    border: 1px solid #d9d9d9;
    border-radius: 8px;
    text-align: center;
    height: 20px;
    background-color: #f2f2f2;
    color: #0a0a0a;
}

QProgressBar::chunk {
    background-color: #0a0a0a;
    border-radius: 8px;
}

/* Generic cards for legacy frames */
#conversionFrame {
    background-color: #ffffff;
    border: 1px solid #e6e6e6;
    border-radius: 16px;
}

#versionComboBox {
    background-color: #ffffff;
}

#warningLabel {
    color: #555;
    font-size: 12px;
}

#closeButton {
    background-color: #ffffff;
    color: #0a0a0a;
    border: 1px solid #0a0a0a;
    border-radius: 10px;
    padding: 8px 14px;
    font-weight: 600;
}

QScrollBar:vertical {
    width: 10px;
    background: transparent;
    margin: 4px 2px 4px 2px;
}
QScrollBar::handle:vertical {
    background: #c7c7c7;
    border-radius: 5px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: #a9a9a9;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QScrollBar:horizontal {
    height: 10px;
    background: transparent;
    margin: 2px 4px 2px 4px;
}
QScrollBar::handle:horizontal {
    background: #c7c7c7;
    border-radius: 5px;
    min-width: 30px;
}
QScrollBar::handle:horizontal:hover {
    background: #a9a9a9;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}
'''
    window.setStyleSheet(style_sheet)











