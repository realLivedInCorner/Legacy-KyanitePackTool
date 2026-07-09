# -*- coding: utf-8 -*-
"""
Custom widgets for the app UI (extracted from ui.py)
"""

import sys
import os
import shutil
import json
import resource_rc

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QTextEdit,
                             QFrame, QGridLayout, QGroupBox, QFileDialog, QProgressBar, QComboBox, QSizePolicy, QColorDialog, QScrollArea, QDialog, QCheckBox, QMessageBox, QLineEdit, QMenu, QToolBar, QMenuBar, QTabWidget)
from PySide6.QtCore import Qt, QSize, QRect, Signal, QThread, QObject
from PySide6.QtWidgets import QStyle
from PySide6.QtGui import QFont, QPalette, QColor, QIcon, QPainter, QBrush, QPen, QTextCharFormat, QTextCursor, QIntValidator, QAction
class ColorDisc(QPushButton):
    def __init__(self):
        super().__init__()
        self.setObjectName("colorDisc")
        self.setFixedSize(48, 48)
        # 美化样式，使用PySide6兼容的样式
        self.setStyleSheet("""
            #colorDisc {
                border-radius: 24px;
                background-color: #f0f0f0;
                border: 2px solid #d0d0d0;
            }
            #colorDisc:hover {
                border-color: #0078d4;
                background-color: #f8f9fa;
            }
        """)
        self.current_color = "浅灰色"
        self.color_object = QColor(240, 240, 240)  # 存储实际的颜色对象，默认为浅灰色
        # 扩展颜色映射，增加更多常用颜色
        self.color_map = {
            "透明": "transparent",
            "白色": "#ffffff",
            "黑色": "#000000",
            "灰色": "#808080",
            "红色": "#ff0000",
            "绿色": "#00ff00",
            "蓝色": "#0000ff",
            "黄色": "#ffff00",
            "紫色": "#800080",
            "青色": "#00ffff",
            "橙色": "#ff8000"
        }
        self.clicked.connect(self.show_color_dialog)
        # 添加颜色名称标签
        self.color_label = QLabel(self.current_color, self)
        self.color_label.setStyleSheet("color: #333333; font-size: 8px; font-weight: bold;")
        self.color_label.setAlignment(Qt.AlignCenter)
        self.color_label.setGeometry(0, 30, 48, 15)
    
    def show_color_dialog(self):
        color_dialog = QColorDialog()
        color_dialog.setWindowTitle("选择背景颜色")
        
        # 设置预定义颜色为中文
        color_dialog.setCustomColor(0, QColor(255, 255, 255))  # 白色
        color_dialog.setCustomColor(1, QColor(0, 0, 0))       # 黑色
        color_dialog.setCustomColor(2, QColor(128, 128, 128)) # 灰色
        color_dialog.setCustomColor(3, QColor(255, 0, 0))     # 红色
        color_dialog.setCustomColor(4, QColor(0, 255, 0))     # 绿色
        color_dialog.setCustomColor(5, QColor(0, 0, 255))     # 蓝色
        color_dialog.setCustomColor(6, QColor(255, 255, 0))   # 黄色
        color_dialog.setCustomColor(7, QColor(255, 0, 255))   # 紫色
        color_dialog.setCustomColor(8, QColor(0, 255, 255))   # 青色
        color_dialog.setCustomColor(9, QColor(255, 128, 0))   # 橙色
        
        if color_dialog.exec():
            color = color_dialog.currentColor()
            self.color_object = color  # 保存实际的颜色对象
            # 更新按钮背景色
            if color.alpha() == 0:
                self.current_color = "透明"
                self.setStyleSheet("""
                    #colorDisc {
                        border-radius: 24px;
                        background-color: transparent;
                        border: 2px dashed #e0e0e0;
                    }
                    #colorDisc:hover {
                        border-color: #0078d4;
                        background-color: #f8f9fa;
                    }
                """)
            else:
                # 检查是否是预定义颜色
                color_name = "自定义"
                for name, hex_color in self.color_map.items():
                    if name != "透明" and QColor(hex_color) == color:
                        color_name = name
                        break
                
                self.current_color = color_name
                style = "#colorDisc {{border-radius: 24px; background-color: {0}; border: 2px solid #e0e0e0;}} #colorDisc:hover {{border-color: #0078d4; background-color: #f8f9fa;}}"
                style = style.format(color.name())
                self.setStyleSheet(style)
            # 更新颜色标签文本
            self.color_label.setText(self.current_color)
    
    def get_rgba(self):
        """
    获取当前颜色的RGBA分量，每个分量的范围是0.0-1.0
    """
        if self.color_object.isValid():
            return {
                "r": self.color_object.redF(),   # 红色分量 (0.0-1.0)
                "g": self.color_object.greenF(), # 绿色分量 (0.0-1.0)
                "b": self.color_object.blueF(),  # 蓝色分量 (0.0-1.0)
                "a": self.color_object.alphaF()  # 透明度 (0.0-1.0)
            }
        else:
            # 如果颜色无效，返回默认的白色RGBA值
            return {
                "r": 1.0,
                "g": 1.0,
                "b": 1.0,
                "a": 1.0
            }

# 其他选项对话框




