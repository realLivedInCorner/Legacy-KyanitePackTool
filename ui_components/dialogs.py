# -*- coding: utf-8 -*-
"""
Dialog windows for the app UI (extracted from ui.py)
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

def apply_unified_dialog_style(dialog):
    dialog.setStyleSheet(dialog.styleSheet() + """
        QDialog {
            background-color: #ffffff;
            border: 1px solid #e6e6e6;
            border-radius: 16px;
        }
        QLabel {
            color: #111111;
        }
        QGroupBox {
            border: 1px solid #eeeeee;
            border-radius: 12px;
            margin-top: 10px;
        }
        QGroupBox::title {
            padding: 0 6px;
            color: #111111;
        }
        QPushButton {
            background-color: #f8f8f8;
            color: #0a0a0a;
            border: 1px solid #dcdcdc;
            border-radius: 18px;
            padding: 6px 16px;
            font-weight: 600;
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
        QLineEdit,
        QTextEdit,
        QComboBox {
            border: 1px solid #dcdcdc;
            border-radius: 10px;
            padding: 6px 10px;
            background-color: #ffffff;
            color: #111111;
        }
        QCheckBox {
            color: #111111;
        }
        QScrollArea {
            border: none;
        }
    """)

class ModernMessageBox(QDialog):
    """自定义现代化提示窗口"""
    
    # 按钮类型常量
    OK = 0
    YES_NO = 1
    YES_NO_CANCEL = 2
    
    # 图标类型常量
    INFO = 0
    WARNING = 1
    ERROR = 2
    QUESTION = 3
    SUCCESS = 4
    
    def __init__(self, title="提示", message="", parent=None, 
                 icon_type=INFO, button_type=OK, width=400, height=200):
        super().__init__(parent)
        
        # 设置窗口属性
        self.setWindowTitle(title)
        self.setFixedSize(width, height)
        self.setWindowModality(Qt.ApplicationModal)
        
        # 设置窗口图标（使用资源文件中的图标）
        self.setWindowIcon(QIcon(":/resource/icon.ico"))
        apply_unified_dialog_style(self)
        
        # 存储用户选择的按钮
        self.result = None
        
        # 创建UI
        self.init_ui(message, icon_type, button_type)
        
    def init_ui(self, message, icon_type, button_type):
        """
    初始化UI组件
    """
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 25, 30, 25)
        main_layout.setSpacing(20)
        
        # 创建内容区域布局
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        
        # 添加图标
        icon_label = self.create_icon(icon_type)
        content_layout.addWidget(icon_label, alignment=Qt.AlignTop)
        
        # 添加消息文本
        message_label = QLabel(message)
        message_label.setObjectName("messageText")
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        content_layout.addWidget(message_label, 1)
        
        main_layout.addLayout(content_layout)
        
        # 添加按钮区域
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignRight)
        button_layout.setSpacing(12)
        
        # 根据按钮类型添加按钮
        if button_type == self.OK:
            ok_button = self.create_button("确定", "primary")
            ok_button.clicked.connect(self.accept)
            button_layout.addWidget(ok_button)
        elif button_type == self.YES_NO:
            yes_button = self.create_button("是", "primary")
            yes_button.clicked.connect(lambda: self.set_result_and_close(True))
            
            no_button = self.create_button("否", "secondary")
            no_button.clicked.connect(lambda: self.set_result_and_close(False))
            
            button_layout.addWidget(no_button)
            button_layout.addWidget(yes_button)
        elif button_type == self.YES_NO_CANCEL:
            yes_button = self.create_button("是", "primary")
            yes_button.clicked.connect(lambda: self.set_result_and_close(True))
            
            no_button = self.create_button("否", "secondary")
            no_button.clicked.connect(lambda: self.set_result_and_close(False))
            
            cancel_button = self.create_button("取消", "secondary")
            cancel_button.clicked.connect(self.reject)
            
            button_layout.addWidget(cancel_button)
            button_layout.addWidget(no_button)
            button_layout.addWidget(yes_button)
        
        main_layout.addLayout(button_layout)
        
        self.setStyleSheet("""
            QDialog {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
            
            #messageText {
                color: #333;
                font-size: 16px;
                line-height: 1.6;
            }
            
            QPushButton {
                background-color: #f8f8f8;
                color: #0a0a0a;
                border: 1px solid #dcdcdc;
                border-radius: 18px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: 600;
                min-width: 70px;
                max-width: 120px;
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
            
            #primaryButton {
                background-color: #f8f8f8;
                color: #0a0a0a;
                border: 1px solid #dcdcdc;
            }
            
            #primaryButton:hover {
                background-color: #f1f1f1;
                border-color: #cfcfcf;
            }
            
            #primaryButton:pressed {
                background-color: #eaeaea;
                border-color: #c2c2c2;
            }
        """)
    
    def create_icon(self, icon_type):
        """
    根据图标类型创建图标标签
    """
        icon_label = QLabel()
        icon_label.setFixedSize(48, 48)
        
        # 根据图标类型选择样式
        if icon_type == self.INFO:
            icon_label.setStyleSheet("""
                background-color: #e3f2fd;
                border-radius: 24px;
                qproperty-alignment: AlignCenter;
                color: #1976d2;
                font-size: 24px;
                font-weight: bold;
            """)
            icon_label.setText("ℹ")
        elif icon_type == self.WARNING:
            icon_label.setStyleSheet("""
                background-color: #fff3e0;
                border-radius: 24px;
                qproperty-alignment: AlignCenter;
                color: #f57c00;
                font-size: 24px;
                font-weight: bold;
            """)
            icon_label.setText("!")
        elif icon_type == self.ERROR:
            icon_label.setStyleSheet("""
                background-color: #ffebee;
                border-radius: 24px;
                qproperty-alignment: AlignCenter;
                color: #d32f2f;
                font-size: 24px;
                font-weight: bold;
            """)
            icon_label.setText("×")
        elif icon_type == self.QUESTION:
            icon_label.setStyleSheet("""
                background-color: #e8f5e9;
                border-radius: 24px;
                qproperty-alignment: AlignCenter;
                color: #388e3c;
                font-size: 24px;
                font-weight: bold;
            """)
            icon_label.setText("?")
        elif icon_type == self.SUCCESS:
            icon_label.setStyleSheet("""
                background-color: #e8f5e9;
                border-radius: 24px;
                qproperty-alignment: AlignCenter;
                color: #388e3c;
                font-size: 24px;
                font-weight: bold;
            """)
            icon_label.setText("✓")
        
        return icon_label
    
    def create_button(self, text, button_type="secondary"):
        """
    创建按钮
    """
        button = QPushButton(text)
        if button_type == "primary":
            button.setObjectName("primaryButton")
            button.setProperty("class", "primary-button")
        else:
            button.setObjectName("secondaryButton")
            button.setProperty("class", "secondary-button")
        return button
    
    def set_result_and_close(self, result):
        """
    设置结果并关闭窗口
    """
        self.result = result
        self.accept()
    
    def exec_(self):
        """
    重写exec_方法，返回用户选择的结果
    """
        super().exec()
        return self.result
    
    # 静态方法，提供简便的API
    @staticmethod
    def info(parent, title, message):
        """
    显示信息提示框
    """
        msg_box = ModernMessageBox(title, message, parent, ModernMessageBox.INFO)
        return msg_box.exec_()
    
    @staticmethod
    def warning(parent, title, message):
        """
    显示警告提示框
    """
        msg_box = ModernMessageBox(title, message, parent, ModernMessageBox.WARNING)
        return msg_box.exec_()
    
    @staticmethod
    def error(parent, title, message):
        """
    显示错误提示框
    """
        msg_box = ModernMessageBox(title, message, parent, ModernMessageBox.ERROR)
        return msg_box.exec_()
    
    @staticmethod
    def question(parent, title, message):
        """
    显示询问提示框
    """
        msg_box = ModernMessageBox(title, message, parent, ModernMessageBox.QUESTION, ModernMessageBox.YES_NO)
        return msg_box.exec_()
    
    @staticmethod
    def success(parent, title, message):
        """
    显示成功提示框
    """
        msg_box = ModernMessageBox(title, message, parent, ModernMessageBox.SUCCESS)
        return msg_box.exec_()

# 主题色功能已移除

# 物品大小对话框类

class ItemSizeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("自定义物品大小")
        self.setFixedSize(1000, 700)  # 窗口大小
        self.setWindowModality(Qt.ApplicationModal)  # 模态对话框
        
        # 设置窗口图标（使用资源文件中的图标）
        self.setWindowIcon(QIcon(":/resource/icon.ico"))
        
        # 创建物品控件字典
        self.item_widgets = {}
        
        # 设置样式
        self.setStyleSheet("""
            QDialog {
                font-family: 'Microsoft YaHei', sans-serif;
                background-color: #f0f0f0;
            }
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 8px;
                background-color: white;
                color: #0a0a0a;
            }
            QScrollArea {
                border: none;
                background-color: #f0f0f0;
            }
            QScrollArea QWidget {
                background-color: #f0f0f0;
            }
            .itemRow {
                background-color: white;
                border-radius: 8px;
                margin-bottom: 10px;
                padding: 12px;
                border: 1px solid #ddd;
            }
            .itemNameLabel {
                font-size: 14px;
                font-weight: 500;
                color: #333;
                background-color: transparent;
                border: none;
                padding: 0;
            }
            .scaleComboBox {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: white;
                color: #333;
            }
            .scaleComboBox:hover {
                border-color: #0078d4;
                background-color: #f8f9fa;
            }
            .headerLabel {
                font-size: 16px;
                font-weight: bold;
                color: #0078d4;
                margin-bottom: 15px;
            }
            QPushButton {
                background-color: #f8f8f8;
                color: #0a0a0a;
                border: 1px solid #dcdcdc;
                border-radius: 18px;
                padding: 6px 16px;
                font-weight: 600;
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
            #startConversionButton {
                background-color: #f8f8f8;
                color: #0a0a0a;
                border: 1px solid #dcdcdc;
            }
            #startConversionButton:hover {
                background-color: #f1f1f1;
                border-color: #cfcfcf;
            }
            #startConversionButton:pressed {
                background-color: #eaeaea;
                border-color: #c2c2c2;
            }
        """)
        
        # 创建主布局
        main_layout = QVBoxLayout(self)
        
        # 创建搜索栏
        search_frame = QFrame()
        search_layout = QHBoxLayout(search_frame)
        search_label = QLabel("搜索物品：")
        search_label.setObjectName("subtitleLabel")
        self.search_input = QTextEdit()
        self.search_input.setMaximumHeight(50)
        self.search_input.setPlaceholderText("输入物品名称进行搜索...")
        self.search_input.textChanged.connect(self.filter_items)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        
        # 创建列表标题
        header_label = QLabel("物品列表")
        header_label.setProperty("class", "headerLabel")
        
        # 创建列表区域，使用QScrollArea实现滚动
        self.scroll_area = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_area)
        
        # 添加表头
        header_frame = QFrame()
        header_frame.setProperty("class", "itemRow")
        header_frame.setStyleSheet("background-color: #f8f9fa;")
        header_layout = QHBoxLayout(header_frame)
        
        item_name_header = QLabel("物品名")
        item_name_header.setFixedWidth(400)
        item_name_header.setProperty("class", "headerLabel")
        
        handheld_scale_header = QLabel("手持放大")
        handheld_scale_header.setFixedWidth(150)
        handheld_scale_header.setProperty("class", "headerLabel")
        
        dropped_scale_header = QLabel("凋落物放大")
        dropped_scale_header.setFixedWidth(150)
        dropped_scale_header.setProperty("class", "headerLabel")
        
        header_layout.addWidget(item_name_header)
        header_layout.addWidget(handheld_scale_header)
        header_layout.addWidget(dropped_scale_header)
        
        # 添加表头到滚动布局
        self.scroll_layout.addWidget(header_frame)
        
        # 添加示例物品数据
        self.add_sample_items()
        
        # 加载保存的设置
        self.load_saved_settings()
        
        # 将滚动区域添加到QScrollArea
        self.scroll_area_widget = QWidget()
        self.scroll_area_widget.setLayout(self.scroll_layout)
        
        self.scroll_area_container = QScrollArea()
        self.scroll_area_container.setWidgetResizable(True)
        self.scroll_area_container.setWidget(self.scroll_area_widget)
        
        # 添加底部按钮区域
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignRight)
        
        save_button = QPushButton("保存")
        save_button.setObjectName("startConversionButton")
        save_button.clicked.connect(self.save_settings)
        
        cancel_button = QPushButton("取消")
        cancel_button.setObjectName("startConversionButton")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        
        # 添加到主布局
        main_layout.addWidget(search_frame)
        main_layout.addWidget(header_label)
        main_layout.addWidget(self.scroll_area_container)
        main_layout.addLayout(button_layout)
    
    def add_sample_items(self):
        # 初始化存储物品控件的数据结构
        self.item_widgets = {}
        
        # 创建物品名称翻译映射
        self.item_translations = {
            "anvil": "铁砧",
            "book": "书",
            "chipped_anvil": "开裂的铁砧",
            "cobweb": "蜘蛛网",
            "compass": "指南针",
            "damaged_anvil": "损坏的铁砧",
            "elytra": "鞘翅",
            "enchanted_golden_apple": "附魔金苹果",
            "enchanting_table": "附魔台",
            "ender_pearl": "末影珍珠",
            "experience_bottle": "附魔之瓶",
            "firework_rocket": "烟花火箭",
            "golden_apple": "金苹果",
            "golden_axe": "金斧",
            "netherite_sword": "下界合金剑",
            "player_head": "玩家头颅",
            "shield": "盾牌",
            "shield_blocking": "格挡下的盾牌",
            "slime_ball": "粘液球",
            "splash_potion": "喷溅药水",
            "totem_of_undying": "不死图腾",
            "trident": "三叉戟",
            "water_bucket": "水桶",
            "block": "方块"
        }
        
        # 重新组织物品数据，分为放大物品和缩小物品
        
        # 添加放大物品分类标题
        zoom_in_label = QLabel("放大物品")
        zoom_in_label.setProperty("class", "headerLabel")
        zoom_in_label.setStyleSheet("margin-top: 10px;")
        self.scroll_layout.addWidget(zoom_in_label)
        
        # 放大物品列表（移除了handheld_rod，并将totem_of_undying移到缩小物品列表）
        zoom_in_items = [
            "anvil", "book", "chipped_anvil", "cobweb", "compass", 
            "damaged_anvil", "elytra", "enchanted_golden_apple",
            "enchanting_table", "ender_pearl", "experience_bottle", "firework_rocket",
            "golden_apple", "golden_axe",
            "netherite_sword", "player_head", "slime_ball",
            "splash_potion", "trident", "water_bucket"
        ]
        
        for item_name in zoom_in_items:
            # 创建物品行框架
            item_frame = QFrame()
            item_frame.setProperty("class", "itemRow")
            item_row = QHBoxLayout(item_frame)
            
            # 创建物品名称标签，显示中文名称
            display_name = self.item_translations.get(item_name, item_name)
            item_label = QLabel(display_name)
            item_label.setFixedWidth(400)
            item_label.setProperty("class", "itemNameLabel")
            # 存储英文名称以便后续保存使用
            item_label.setObjectName(item_name)
            
            # 创建手持放大倍数下拉框
            handheld_combo = QComboBox()
            handheld_combo.setFixedWidth(150)
            handheld_combo.setProperty("class", "scaleComboBox")
            handheld_combo.addItems(["1x", "2x", "3x", "4x"])
            handheld_combo.setCurrentText("1x")
            
            # 创建凋落物放大倍数下拉框
            dropped_combo = QComboBox()
            dropped_combo.setFixedWidth(150)
            dropped_combo.setProperty("class", "scaleComboBox")
            dropped_combo.addItems(["1x", "2x", "3x", "4x"])
            dropped_combo.setCurrentText("1x")
            
            # 添加到物品行布局
            item_row.addWidget(item_label)
            item_row.addWidget(handheld_combo)
            item_row.addWidget(dropped_combo)
            
            # 将物品行添加到滚动区域布局
            self.scroll_layout.addWidget(item_frame)
            
            # 存储控件引用以便后续获取设置
            self.item_widgets[item_name] = {
                "type": "zoom_in",
                "handheld_combo": handheld_combo,
                "dropped_combo": dropped_combo
            }
        
        # 添加缩小物品分类标题
        zoom_out_label = QLabel("缩小物品")
        zoom_out_label.setProperty("class", "headerLabel")
        zoom_out_label.setStyleSheet("margin-top: 20px;")
        self.scroll_layout.addWidget(zoom_out_label)
        
        # 缩小物品列表（移除了generated.json，并添加了totem_of_undying）
        zoom_out_items = ["block",  "shield", "shield_blocking", "totem_of_undying"]
        
        for item_name in zoom_out_items:
            # 创建物品行框架
            item_frame = QFrame()
            item_frame.setProperty("class", "itemRow")
            item_row = QHBoxLayout(item_frame)
            
            # 创建物品名称标签，显示中文名称
            display_name = self.item_translations.get(item_name, item_name)
            item_label = QLabel(display_name)
            item_label.setFixedWidth(400)
            item_label.setProperty("class", "itemNameLabel")
            # 存储英文名称以便后续保存使用
            item_label.setObjectName(item_name)
            
            # 创建复选框用于确认是否缩小（占据两列宽度）
            shrink_check = QCheckBox("是否缩小")
            shrink_check.setChecked(False)
            
            # 创建一个水平布局来容纳复选框，使其占据两列宽度
            checkbox_layout = QHBoxLayout()
            checkbox_layout.setAlignment(Qt.AlignLeft)
            checkbox_layout.addWidget(shrink_check)
            
            # 添加到物品行布局
            item_row.addWidget(item_label)
            item_row.addLayout(checkbox_layout, 2)  # 占据2个单位的空间
            
            # 将物品行添加到滚动区域布局
            self.scroll_layout.addWidget(item_frame)
            
            # 存储控件引用以便后续获取设置
            self.item_widgets[item_name] = {
                "type": "zoom_out",
                "shrink_check": shrink_check
            }
    
    def add_item_row(self, item_name):
        # 创建物品行
        item_frame = QFrame()
        item_frame.setObjectName("itemRowFrame")
        item_frame.setStyleSheet("""
            #itemRowFrame {
                border-bottom: 1px solid #f0f0f0;
            }
        """)
        item_layout = QHBoxLayout(item_frame)
        
        # 物品名称
        item_label = QLabel(item_name)
        item_label.setFixedWidth(400)
        
        # 放大倍数选择
        scale_combo = QComboBox()
        scale_combo.setObjectName("scaleComboBox")
        scales = ["1x", "2x", "4x", "8x", "16x"]
        scale_combo.addItems(scales)
        scale_combo.setCurrentText("2x")
        
        item_layout.addWidget(item_label)
        item_layout.addWidget(scale_combo)
        
        # 添加到滚动布局
        self.scroll_layout.addWidget(item_frame)
    
    def filter_items(self):
        # 搜索过滤逻辑
        search_text = self.search_input.toPlainText().lower()
        
        # 获取所有物品行（跳过第一个是表头）
        for i in range(1, self.scroll_layout.count()):
            item_frame = self.scroll_layout.itemAt(i).widget()
            if item_frame:
                # 获取物品名称标签
                item_layout = item_frame.layout()
                if item_layout:
                    item_label = item_layout.itemAt(0).widget()
                    if item_label and isinstance(item_label, QLabel):
                        # 检查物品名称是否包含搜索文本（中文名称或英文名称）
                        chinese_name = item_label.text().lower()
                        english_name = item_label.objectName().lower()
                        
                        if search_text in chinese_name or search_text in english_name:
                            item_frame.show()
                        else:
                            item_frame.hide()
    
    def load_saved_settings(self):
        """
    从overlay.json文件加载保存的设置到自定义物品大小窗口
    """
        import json
        import os
        
        # 始终使用同一个固定位置的overlay.json文件
        temp_overlay_dir = os.path.join(os.getcwd(), "temp_overlay")
        overlay_file = os.path.join(temp_overlay_dir, "overlay.json")
        
        # 如果文件不存在，不执行加载
        if not os.path.exists(overlay_file):
            return
        
        try:
            # 使用utf-8-sig编码读取文件，确保能正确解析BOM
            with open(overlay_file, "r", encoding="utf-8-sig") as f:
                settings = json.load(f)
            
            # 支持新键名core_item_scaling和旧键名big_item、small_item的向后兼容性
            big_items = {}
            small_items = {}
            
            # 先检查是否有新的core_item_scaling设置
            if "core_item_scaling" in settings:
                core_item_scaling = settings["core_item_scaling"]
                if "big_item" in core_item_scaling:
                    big_items = core_item_scaling["big_item"]
                if "small_item" in core_item_scaling:
                    small_items = core_item_scaling["small_item"]
            # 如果没有新设置，回退到旧的顶层设置
            elif "big_item" in settings:
                big_items = settings["big_item"]
            if "small_item" in settings:
                small_items = settings["small_item"]
            
            # 应用放大物品的设置
            for item_name, item_data in big_items.items():
                if item_name in self.item_widgets and self.item_widgets[item_name]["type"] == "zoom_in":
                    item_widget = self.item_widgets[item_name]
                    if "handheld_scale" in item_data:
                        if item_data["handheld_scale"] in ["1x", "2x", "3x", "4x"]:
                            item_widget["handheld_combo"].setCurrentText(item_data["handheld_scale"])
                    if "dropped_scale" in item_data:
                        if item_data["dropped_scale"] in ["1x", "2x", "3x", "4x"]:
                            item_widget["dropped_combo"].setCurrentText(item_data["dropped_scale"])
            
            # 应用缩小物品的设置
            for item_name, item_data in small_items.items():
                if item_name in self.item_widgets and self.item_widgets[item_name]["type"] == "zoom_out":
                    item_widget = self.item_widgets[item_name]
                    if "should_shrink" in item_data:
                        item_widget["shrink_check"].setChecked(item_data["should_shrink"])
        except Exception as e:
            ModernMessageBox.warning(self, "加载失败", f"加载设置时出错: {str(e)}")
    
    def save_settings(self):
        """
    保存用户在自定义物品大小窗口中设置的选项到overlay.json文件
    """
        import json
        import os
        
        # 收集设置
        settings = {}
        
        # 分离放大和缩小的物品设置
        big_items = {}
        small_items = {}
        
        for item_name, item_data in self.item_widgets.items():
            if item_data["type"] == "zoom_in":
                big_items[item_name] = {
                    "type": "zoom_in",
                    "handheld_scale": item_data["handheld_combo"].currentText(),
                    "dropped_scale": item_data["dropped_combo"].currentText()
                }
            elif item_data["type"] == "zoom_out" and item_data["shrink_check"].isChecked():
                small_items[item_name] = {
                    "type": "zoom_out",
                    "should_shrink": True
                }
        
        # 如果有放大的物品，添加到big_item名称下
        if big_items:
            settings["big_item"] = big_items
        
        # 如果有缩小的物品，添加到small_item名称下
        if small_items:
            settings["small_item"] = small_items
        
        # 检查父窗口是否有color_disc属性，获取背景颜色的RGBA分量
        if hasattr(self.parent(), 'color_disc'):
            color_disc = self.parent().color_disc
            # 获取颜色的RGBA分量（0.0-1.0范围）
            settings["nametag"] = {
                "color": color_disc.get_rgba(),
                "enabled": True
            }
        
        # 创建temp_overlay文件夹
        temp_overlay_dir = os.path.join(os.getcwd(), "temp_overlay")
        os.makedirs(temp_overlay_dir, exist_ok=True)
        
        # 始终使用同一个固定位置的overlay.json文件
        overlay_file = os.path.join(temp_overlay_dir, "overlay.json")
        
        # 如果文件已存在，先读取现有内容
        if os.path.exists(overlay_file):
            try:
                with open(overlay_file, "r", encoding="utf-8-sig") as f:
                    existing_settings = json.load(f)
                # 合并新的设置
                existing_settings.update(settings)
                settings = existing_settings
            except json.JSONDecodeError:
                # 如果文件格式错误，则创建新的设置对象
                existing_settings = {}
                settings = existing_settings
        
        # 写入文件，确保中文字符正确编码
        with open(overlay_file, "w", encoding="utf-8-sig") as f:
            json.dump(settings, f, ensure_ascii=False, indent=4, separators=(',', ': '))
        
        # 提示保存成功
        ModernMessageBox.success(self, "保存成功", f"设置已成功保存到 {overlay_file}")
        
        # 关闭对话框
        self.accept()

class CustomNameDialog(QDialog):
    # Minecraft 颜色和格式代码映射
    COLOR_CODES = {
        "黑色": "§0",
        "深蓝色": "§1",
        "深绿色": "§2",
        "深青色": "§3",
        "深红色": "§4",
        "紫色": "§5",
        "金色": "§6",
        "灰色": "§7",
        "深灰色": "§8",
        "蓝色": "§9",
        "绿色": "§a",
        "青色": "§b",
        "红色": "§c",
        "粉红色": "§d",
        "黄色": "§e",
        "白色": "§f"
    }
    
    # 颜色代码到实际颜色的映射
    CODE_TO_COLOR = {
        "§0": "#000000",  # 黑色
        "§1": "#0000AA",  # 深蓝色
        "§2": "#00AA00",  # 深绿色
        "§3": "#00AAAA",  # 深青色
        "§4": "#AA0000",  # 深红色
        "§5": "#AA00AA",  # 紫色
        "§6": "#FFAA00",  # 金色
        "§7": "#AAAAAA",  # 灰色
        "§8": "#555555",  # 深灰色
        "§9": "#5555FF",  # 蓝色
        "§a": "#55FF55",  # 绿色
        "§b": "#55FFFF",  # 青色
        "§c": "#FF5555",  # 红色
        "§d": "#FF55FF",  # 粉红色
        "§e": "#FFFF55",  # 黄色
        "§f": "#FFFFFF"   # 白色
    }
    
    FORMAT_CODES = {
        "随机": "§k",
        "粗体": "§l",
        "删除线": "§m",
        "下划线": "§n",
        "斜体": "§o",
        "重置": "§r"
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("自定义物品名称")
        # 设置最小尺寸但不固定最大尺寸，允许窗口适当扩展
        self.resize(600, 550)  # 初始尺寸
        self.setMinimumSize(600, 550)
        
        # 设置窗口图标（使用资源文件中的图标）
        self.setWindowIcon(QIcon(":/resource/icon.ico"))
        apply_unified_dialog_style(self)
        
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        # 标题
        title = QLabel("自定义物品名称")
        title.setObjectName("welcomeTitle")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # 语言选择区域
        language_frame = QFrame()
        language_layout = QHBoxLayout(language_frame)
        language_layout.setContentsMargins(0, 0, 0, 0)
        language_layout.setSpacing(30)
        
        language_label = QLabel("选择语言：")
        language_label.setObjectName("dragDropLabel")
        
        # 创建中英文复选框
        self.english_checkbox = QCheckBox("英文")
        self.chinese_checkbox = QCheckBox("中文")
        
        # 默认选择中文
        self.chinese_checkbox.setChecked(True)
        
        # 连接信号，确保只有一个被选中
        self.english_checkbox.toggled.connect(lambda: self.on_language_checkbox_toggled(self.english_checkbox))
        self.chinese_checkbox.toggled.connect(lambda: self.on_language_checkbox_toggled(self.chinese_checkbox))
        
        language_layout.addWidget(language_label)
        language_layout.addWidget(self.english_checkbox)
        language_layout.addWidget(self.chinese_checkbox)
        language_layout.addStretch()
        
        main_layout.addWidget(language_frame)
        
        # 创建滚动区域并保存为实例变量
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # 滚动区域的内容
        self.scroll_content = QWidget()
        scroll_layout = QVBoxLayout(self.scroll_content)
        scroll_layout.setSpacing(10)
        
        # 创建物品名称映射字典和格式化代码映射字典
        self.name_mappings = {}  # 存储QTextEdit引用
        self.format_codes = {}  # 存储包含格式化代码的原始文本
        
        # 添加滚动内容到滚动区域
        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area)
        
        # 底部按钮区域
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignRight)
        
        save_button = QPushButton("保存")
        save_button.setObjectName("startConversionButton")
        save_button.clicked.connect(self.save_settings)
        
        cancel_button = QPushButton("取消")
        cancel_button.setObjectName("startConversionButton")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        
        main_layout.addLayout(button_layout)
        
        # 初始化物品名称列表
        self.initialize_item_list()
        
        # 加载已保存的设置
        self.load_saved_settings()
    
    def initialize_item_list(self):
        """
    根据选择的语言初始化物品名称列表，按类别组织显示
    """
        # 导入必要的模块
        import os
        import json
        
        # 重置映射字典
        self.name_mappings = {}
        self.format_codes = {}
        self.item_id_map = {}
        
        # 清空现有的内容
        scroll_layout = self.scroll_content.layout()
        while scroll_layout.count() > 0:
            item = scroll_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.hide()
                widget.deleteLater()
        
        # 确定使用的语言文件
        use_chinese = self.chinese_checkbox.isChecked()
        lang_file = "zh_cn.json" if use_chinese else "en_us.json"
        lang_file_path = os.path.join(os.getcwd(), "lang", lang_file)
        
        # 按类别组织物品ID列表
        item_categories = {
            "工具与武器": [
                "item.minecraft.diamond_sword", "item.minecraft.diamond_axe", "item.minecraft.diamond_pickaxe",
                "item.minecraft.diamond_shovel", "item.minecraft.diamond_hoe",
                "item.minecraft.iron_sword", "item.minecraft.iron_axe", "item.minecraft.iron_pickaxe",
                "item.minecraft.iron_shovel", "item.minecraft.iron_hoe",
                "item.minecraft.netherite_sword", "item.minecraft.netherite_axe", "item.minecraft.netherite_pickaxe",
                "item.minecraft.netherite_shovel", "item.minecraft.netherite_hoe",
                "item.minecraft.golden_sword", "item.minecraft.golden_axe", "item.minecraft.golden_pickaxe",
                "item.minecraft.golden_shovel", "item.minecraft.golden_hoe",
                "item.minecraft.stone_sword", "item.minecraft.stone_axe", "item.minecraft.stone_pickaxe",
                "item.minecraft.stone_shovel", "item.minecraft.stone_hoe",
                "item.minecraft.wooden_sword", "item.minecraft.wooden_axe", "item.minecraft.wooden_pickaxe",
                "item.minecraft.wooden_shovel", "item.minecraft.wooden_hoe",
                "item.minecraft.bow", "item.minecraft.crossbow", "item.minecraft.trident",
                "item.minecraft.fishing_rod", "item.minecraft.shears"
            ],
            "盔甲": [
                "item.minecraft.diamond_helmet", "item.minecraft.diamond_chestplate", "item.minecraft.diamond_leggings", "item.minecraft.diamond_boots",
                "item.minecraft.iron_helmet", "item.minecraft.iron_chestplate", "item.minecraft.iron_leggings", "item.minecraft.iron_boots",
                "item.minecraft.netherite_helmet", "item.minecraft.netherite_chestplate", "item.minecraft.netherite_leggings", "item.minecraft.netherite_boots",
                "item.minecraft.golden_helmet", "item.minecraft.golden_chestplate", "item.minecraft.golden_leggings", "item.minecraft.golden_boots",
                "item.minecraft.chainmail_helmet", "item.minecraft.chainmail_chestplate", "item.minecraft.chainmail_leggings", "item.minecraft.chainmail_boots",
                "item.minecraft.shield", "item.minecraft.elytra"
            ],
            "材料": [
                "item.minecraft.diamond", "item.minecraft.netherite_ingot", "item.minecraft.emerald",
                "item.minecraft.iron_ingot", "item.minecraft.gold_ingot",
                "item.minecraft.raw_iron", "item.minecraft.raw_gold", "item.minecraft.raw_copper",
                "item.minecraft.stick"
            ],
            "消耗品与其他": [
                "item.minecraft.apple", "item.minecraft.golden_apple", "item.minecraft.enchanted_golden_apple",
                "item.minecraft.bread", "item.minecraft.egg", "item.minecraft.feather",
                "item.minecraft.ender_pearl", "item.minecraft.experience_bottle", "item.minecraft.slime_ball",
                "item.minecraft.snowball", "item.minecraft.book", "item.minecraft.blaze_rod",
                "item.minecraft.end_crystal", "item.minecraft.bucket", "item.minecraft.water_bucket", "item.minecraft.lava_bucket",
                "item.minecraft.clock", "item.minecraft.compass", "item.minecraft.bowl"
            ]
        }
        
        # 加载语言文件
        lang_data = {}
        try:
            with open(lang_file_path, "r", encoding="utf-8-sig") as f:
                lang_data = json.load(f)
        except Exception as e:
            print(f"加载语言文件失败: {e}")
        
        # 处理每个类别的物品
        for category, item_ids in item_categories.items():
            # 添加类别标题
            category_label = QLabel(category)
            category_label.setObjectName("categoryTitle")
            category_label.setStyleSheet(
                "font-weight: bold; font-size: 14px; margin-top: 15px; margin-bottom: 5px; color: #333;")
            scroll_layout.addWidget(category_label)
            
            # 创建类别框架，为每个类别添加背景色以区分
            category_frame = QFrame()
            category_frame.setStyleSheet("background-color: #f9f9f9; border-radius: 5px; padding: 5px;")
            category_layout = QVBoxLayout(category_frame)
            category_layout.setContentsMargins(5, 5, 5, 5)
            category_layout.setSpacing(5)
            
            # 添加类别内的物品
            for item_id in item_ids:
                # 获取物品名称
                item_name = ""  
                if item_id in lang_data:
                    item_name = lang_data[item_id]
                    self.item_id_map[item_name] = item_id
                else:
                    # 从物品ID中提取名称作为备选
                    item_name = item_id.replace("item.minecraft.", "").replace("_", " ").title()
                    self.item_id_map[item_name] = item_id
                
                if item_name:
                    # 创建行容器
                    row_widget = QWidget()
                    row_widget.setMinimumHeight(38)
                    row_widget.setMaximumHeight(48)
                    row_widget.setStyleSheet("background-color: white; border: 1px solid #e0e0e0; border-radius: 3px;")
                    
                    # 创建行布局
                    row_layout = QHBoxLayout(row_widget)
                    row_layout.setContentsMargins(10, 5, 10, 5)
                    row_layout.setSpacing(15)
                    
                    # 原名称标签
                    original_name_label = QLabel(item_name)
                    original_name_label.setMinimumWidth(150)
                    original_name_label.setMaximumWidth(150)
                    original_name_label.setStyleSheet("color: #555;")
                    
                    # 使用QTextEdit以支持富文本
                    custom_name_edit = QTextEdit()
                    # 允许水平滚动以显示长文本
                    custom_name_edit.setLineWrapMode(QTextEdit.NoWrap)
                    custom_name_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                    custom_name_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
                    custom_name_edit.setStyleSheet("border: 1px solid #ddd; padding: 3px;")
                    
                    # 连接右键菜单信号
                    custom_name_edit.setContextMenuPolicy(Qt.CustomContextMenu)
                    custom_name_edit.customContextMenuRequested.connect(
                        lambda pos, edit=custom_name_edit, item=item_name: self.show_context_menu(pos, edit, item)
                    )
                    
                    # 连接文本变化信号
                    custom_name_edit.textChanged.connect(
                        lambda edit=custom_name_edit, item=item_name: self.update_format_codes(edit, item)
                    )
                    
                    # 存储引用
                    self.name_mappings[item_name] = custom_name_edit
                    self.format_codes[item_name] = ""
                    
                    # 添加到行布局
                    row_layout.addWidget(original_name_label)
                    row_layout.addWidget(custom_name_edit)
                    
                    # 添加到类别布局
                    category_layout.addWidget(row_widget)
            
            # 添加类别框架到滚动布局
            scroll_layout.addWidget(category_frame)
        
        # 添加一个占位符来确保滚动区域正常工作
        spacer = QWidget()
        spacer.setMinimumHeight(30)
        scroll_layout.addWidget(spacer)
        
        # 强制更新和调整大小
        self.scroll_content.update()
        scroll_layout.update()
        self.scroll_content.adjustSize()
        self.scroll_area.updateGeometry()
    
    def on_language_checkbox_toggled(self, checkbox):
        """
    处理语言复选框切换事件，确保只有一个复选框被选中
    """
        # 确保只有一个复选框被选中
        if checkbox.isChecked():
            if checkbox == self.english_checkbox:
                self.chinese_checkbox.setChecked(False)
            else:
                self.english_checkbox.setChecked(False)
            # 切换语言后重新初始化物品列表
            self.initialize_item_list()
            # 重新加载已保存的设置
            self.load_saved_settings()

    def load_saved_settings(self):
        """
    加载已保存的设置，包括语言偏好和自定义名称
    """
        import json
        import os
        
        # 从固定位置的overlay.json文件中加载设置
        temp_overlay_dir = os.path.join(os.getcwd(), "temp_overlay")
        overlay_file = os.path.join(temp_overlay_dir, "overlay.json")
        
        if os.path.exists(overlay_file):
            try:
                # 使用utf-8-sig编码读取，以支持带BOM的UTF-8文件
                with open(overlay_file, "r", encoding="utf-8-sig") as f:
                    settings = json.load(f)
                
                # 加载保存的语言偏好
                if "selected_language" in settings:
                    selected_language = settings["selected_language"]
                    if selected_language == "zh_cn":
                        self.chinese_checkbox.setChecked(True)
                        self.english_checkbox.setChecked(False)
                    else:
                        self.chinese_checkbox.setChecked(False)
                        self.english_checkbox.setChecked(True)
                
                # 加载自定义物品名称设置（支持新格式'lang_itemname'和旧格式'custom_item_names'）
                if "lang_itemname" in settings:
                    custom_names = settings["lang_itemname"]
                    # 创建一个反向映射，从物品ID映射到显示名称
                    reverse_id_map = {v: k for k, v in self.item_id_map.items()}
                    
                    for key, custom_name in custom_names.items():
                        # 检查key是否是物品ID（以"item.minecraft."开头）
                        if key.startswith("item.minecraft."):
                            # 查找对应的显示名称
                            if key in reverse_id_map and reverse_id_map[key] in self.name_mappings:
                                display_name = reverse_id_map[key]
                                self.format_codes[display_name] = custom_name
                                self.name_mappings[display_name].setPlainText(custom_name)
                        elif key in self.name_mappings:
                            # 如果key不是物品ID，可能是旧格式的显示名称
                            self.format_codes[key] = custom_name
                            self.name_mappings[key].setPlainText(custom_name)
                elif "custom_item_names" in settings:
                    # 向后兼容旧格式
                    custom_names = settings["custom_item_names"]
                    for original_name, custom_name in custom_names.items():
                        if original_name in self.name_mappings:
                            # 保存格式化代码
                            self.format_codes[original_name] = custom_name
                            # 显示到QTextEdit
                            self.name_mappings[original_name].setPlainText(custom_name)
            except Exception as e:
                print(f"加载自定义名称设置失败: {e}")
        
    def show_context_menu(self, position, edit_widget, item_name):
        """
    显示右键菜单，用于选择文本颜色和格式
    """
        # 获取QTextEdit的光标
        cursor = edit_widget.textCursor()
        selected_text = cursor.selectedText()
        
        if not selected_text:
            # 如果没有选中文本，就选中光标位置的整个单词
            cursor.select(QTextCursor.WordUnderCursor)
            selected_text = cursor.selectedText()
            edit_widget.setTextCursor(cursor)
            
        # 创建右键菜单
        menu = QMenu()
        
        # 添加文本选择状态显示
        if selected_text:
            menu.addAction(f"当前选择: '{selected_text}'").setEnabled(False)
        else:
            menu.addAction("未选择任何文本").setEnabled(False)
        
        menu.addSeparator()
        
        # 添加格式化选项组
        
        # 粗体
        bold_action = menu.addAction("粗体 (&B)")
        bold_action.triggered.connect(lambda checked, edit=edit_widget, item=item_name: 
                                      self.apply_formatting("§l", edit, item))
        
        # 斜体
        italic_action = menu.addAction("斜体 (&I)")
        italic_action.triggered.connect(lambda checked, edit=edit_widget, item=item_name: 
                                        self.apply_formatting("§o", edit, item))
        
        # 下划线
        underline_action = menu.addAction("下划线 (&U)")
        underline_action.triggered.connect(lambda checked, edit=edit_widget, item=item_name: 
                                           self.apply_formatting("§n", edit, item))
        
        # 删除线
        strikethrough_action = menu.addAction("删除线 (&S)")
        strikethrough_action.triggered.connect(lambda checked, edit=edit_widget, item=item_name: 
                                               self.apply_formatting("§m", edit, item))
        
        menu.addSeparator()
        
        # 添加颜色选择
        color_menu = menu.addMenu("文本颜色 (&C)")
        
        # 创建颜色菜单项
        for color_name, color_code in self.COLOR_CODES.items():
            color_action = color_menu.addAction(color_name)
            color_action.triggered.connect(lambda checked, code=color_code, edit=edit_widget, item=item_name: 
                                          self.apply_formatting(code, edit, item))
        
        menu.addSeparator()
        
        # 添加快捷操作
        action_menu = menu.addMenu("快捷操作 (&A)")
        
        # 复制原始名称
        copy_original_action = action_menu.addAction("复制原始名称 (&O)")
        copy_original_action.triggered.connect(lambda: self.copy_original_name(item_name))
        
        # 清空内容
        clear_action = action_menu.addAction("清空内容 (&L)")
        clear_action.triggered.connect(lambda: edit_widget.clear())
        
        # 应用默认格式到全部
        apply_default_to_all_action = action_menu.addAction("应用默认格式到全部 (&D)")
        apply_default_to_all_action.triggered.connect(lambda: self.apply_default_format_to_all())
        
        # 在鼠标位置显示菜单
        menu.exec(edit_widget.mapToGlobal(position))
        

    def copy_original_name(self, item_name):
        """
    复制物品的原始名称到剪贴板
    """
        clipboard = QApplication.clipboard()
        clipboard.setText(item_name)
        
    def apply_default_format_to_all(self):
        """
    为所有物品应用默认的格式化样式
    """
        default_format = "§7"  # 默认使用灰色
        
        # 遍历所有物品并应用默认格式
        for item_name, edit_widget in self.name_mappings.items():
            current_text = edit_widget.toPlainText()
            if current_text:
                # 移除所有格式代码
                clean_text = ""
                skip_next = False
                for char in current_text:
                    if skip_next:
                        skip_next = False
                        continue
                    if char == "§":
                        skip_next = True
                        continue
                    clean_text += char
                
                # 应用默认格式
                edit_widget.setPlainText(default_format + clean_text)
                
                # 更新格式化代码
                self.format_codes[item_name] = default_format + clean_text
            
    def apply_formatting(self, format_code, edit_widget, item_name):
        """
    应用文本格式化代码到选中的文本，并在界面上显示实际颜色效果
    """
        # 获取QTextEdit的光标
        cursor = edit_widget.textCursor()
        selected_text = cursor.selectedText()
        
        if selected_text:
            # 保留原始格式化代码
            original_text = self.format_codes.get(item_name, "")
            cursor_pos = cursor.position()
            anchor_pos = cursor.anchor()
            start = min(cursor_pos, anchor_pos)
            end = max(cursor_pos, anchor_pos)
            
            # 提取纯文本内容（不包含格式代码）
            plain_text = ""
            skip_next = False
            for char in original_text:
                if skip_next:
                    skip_next = False
                    continue
                if char == "§":
                    skip_next = True
                    continue
                plain_text += char
            
            # 判断是颜色代码还是格式代码
            color_codes = set(self.COLOR_CODES.values())
            format_codes = set(self.FORMAT_CODES.values()) - {"§r"}  # 排除重置代码
            
            # 判断是否选择了整个字符串
            is_full_string = (start == 0 and end == len(plain_text))
            
            # 构建新的格式化文本
            new_formatted_text = ""
            
            # 计算选中的文本在原始格式化文本中的位置
            # 由于格式代码的存在，需要更精确地计算位置
            current_plain_pos = 0
            i = 0
            
            # 用于标记是否已经处理了选中区域
            processed_selection = False
            
            while i < len(original_text):
                if original_text[i] == "§" and i + 1 < len(original_text):
                    # 处理格式代码
                    new_formatted_text += original_text[i:i+2]
                    i += 2
                else:
                    # 处理普通字符
                    if current_plain_pos >= start and current_plain_pos < end:
                        if not processed_selection:
                            # 开始处理选中区域
                            if format_code in format_codes:
                                # 格式代码：在选中区域前面添加§r
                                new_formatted_text += "§r"
                            
                            # 添加新的格式代码和选中的文本
                            new_formatted_text += format_code
                            
                            # 找出选中区域在原始格式化文本中的实际位置
                            selection_start = i
                            selection_end = i + (end - start)
                            
                            # 复制选中的文本（包括其中的格式代码）
                            j = i
                            temp_plain_pos = current_plain_pos
                            while j < len(original_text) and temp_plain_pos < end:
                                if original_text[j] == "§" and j + 1 < len(original_text):
                                    new_formatted_text += original_text[j:j+2]
                                    j += 2
                                else:
                                    new_formatted_text += original_text[j]
                                    j += 1
                                    temp_plain_pos += 1
                            
                            # 根据代码类型添加重置代码
                            if format_code in format_codes:
                                # 格式代码：在选中区域末尾添加§r
                                new_formatted_text += "§r"
                            elif format_code in color_codes and not is_full_string:
                                # 颜色代码且不是选择整个字符串：仅在尾部添加一个§r
                                new_formatted_text += "§r"
                            
                            # 更新索引
                            i = j
                            current_plain_pos = temp_plain_pos
                            processed_selection = True
                    else:
                        # 处理非选中区域的字符
                        new_formatted_text += original_text[i]
                        i += 1
                        current_plain_pos += 1
            
            # 如果原始文本为空或无法正确处理，则使用简化的处理方式
            if not new_formatted_text or not processed_selection:
                # 根据代码类型添加重置代码
                if format_code in format_codes:
                    # 格式代码：在选中区域前后都添加§r
                    new_formatted_text = original_text[:start] + "§r" + format_code + selected_text + "§r" + original_text[end:]
                elif format_code in color_codes and not is_full_string:
                    # 颜色代码且不是选择整个字符串：仅在尾部添加一个§r
                    new_formatted_text = original_text[:start] + format_code + selected_text + "§r" + original_text[end:]
                else:
                    # 其他情况：正常添加格式代码
                    new_formatted_text = original_text[:start] + format_code + selected_text + original_text[end:]
            
            self.format_codes[item_name] = new_formatted_text
            
            # 应用富文本格式到QTextEdit
            self.apply_rich_text_formatting(format_code, edit_widget)
    
    def apply_rich_text_formatting(self, format_code, edit_widget):
        """
    将格式化代码转换为实际的富文本格式应用到QTextEdit
    """
        cursor = edit_widget.textCursor()
        
        # 创建文本格式
        char_format = QTextCharFormat()
        
        # 应用颜色
        if format_code in self.CODE_TO_COLOR:
            char_format.setForeground(QBrush(QColor(self.CODE_TO_COLOR[format_code])))
        
        # 应用格式
        if format_code == "§l":  # 粗体
            char_format.setFontWeight(QFont.Bold)
        elif format_code == "§o":  # 斜体
            char_format.setFontItalic(True)
        elif format_code == "§n":  # 下划线
            char_format.setFontUnderline(True)
        elif format_code == "§m":  # 删除线
            char_format.setFontStrikeOut(True)
        elif format_code == "§r":  # 重置
            char_format = QTextCharFormat()  # 使用默认格式
        
        # 应用格式到选中的文本
        cursor.mergeCharFormat(char_format)
        edit_widget.setTextCursor(cursor)
            
    def update_format_codes(self, edit_widget, item_name):
        """
    当文本变化时，更新格式化代码存储
    """
        # 获取QTextEdit的纯文本
        plain_text = edit_widget.toPlainText()
        
        # 检查是否已有格式化代码存储
        if item_name in self.format_codes:
            stored_text = self.format_codes[item_name]
            
            # 如果存储的文本包含格式化代码
            has_color_codes = any(code in stored_text for code in self.COLOR_CODES.values())
            has_format_codes = any(code in stored_text for code in self.FORMAT_CODES.values())
            
            if has_color_codes or has_format_codes: 
                # 从存储的文本中提取纯文本（不包含格式代码）
                plain_stored_text = ""
                skip_next = False
                for char in stored_text:
                    if skip_next:
                        skip_next = False
                        continue
                    if char == "§":
                        skip_next = True
                        continue
                    plain_stored_text += char
                
                # 如果纯文本内容相同，仅保留存储的格式化代码文本
                if plain_stored_text.strip() == plain_text.strip():
                    # 内容没有变化，保留格式化代码
                    return
                
                # 内容有变化，但我们仍尝试保留所有格式代码
                # 提取所有格式代码
                all_format_codes = []
                i = 0
                while i < len(stored_text):
                    if stored_text[i] == "§" and i + 1 < len(stored_text):
                        all_format_codes.append(stored_text[i:i+2])
                        i += 2
                    else:
                        i += 1
                
                # 创建新的格式化文本，将所有格式代码应用到新文本
                # 为了简化，我们将所有格式代码应用到整个文本
                if all_format_codes:
                    new_formatted_text = "".join(all_format_codes) + plain_text
                    self.format_codes[item_name] = new_formatted_text
                    return
        
        # 如果没有格式化代码或无法保留格式，则更新为纯文本
        self.format_codes[item_name] = plain_text
        
    def save_settings(self):
        """
    保存用户在自定义名字窗口中设置的选项
    """
        import json
        import os
        
        # 收集设置
        settings = {}
        custom_names = {}
        
        # 收集所有非空的自定义名称（使用存储的格式化代码）
        for original_name in self.name_mappings.keys():
            # 优先使用格式化代码文本
            custom_name = self.format_codes.get(original_name, "").strip()
            
            # 如果格式化代码文本为空，尝试从文本框获取
            if not custom_name:
                edit_widget = self.name_mappings[original_name]
                custom_name = edit_widget.toPlainText().strip()
                
            if custom_name:
                # 使用物品ID作为键保存自定义名称
                if original_name in self.item_id_map:
                    item_id = self.item_id_map[original_name]
                    custom_names[item_id] = custom_name
                else:
                    # 如果找不到对应的物品ID，使用原始名称（向后兼容）
                    custom_names[original_name] = custom_name
        
        # 如果有自定义名称，则添加到设置中
        if custom_names:
            settings["lang_itemname"] = custom_names
            
        # 保存选择的语言
        settings["selected_language"] = "zh_cn" if self.chinese_checkbox.isChecked() else "en_us"
        
        # 创建temp_overlay文件夹
        temp_overlay_dir = os.path.join(os.getcwd(), "temp_overlay")
        os.makedirs(temp_overlay_dir, exist_ok=True)
        
        # 始终使用同一个固定位置的overlay.json文件
        overlay_file = os.path.join(temp_overlay_dir, "overlay.json")
        
        # 如果文件已存在，先读取现有内容
        if os.path.exists(overlay_file):
            try:
                with open(overlay_file, "r", encoding="utf-8-sig") as f:
                    existing_settings = json.load(f)
                # 合并新的自定义名称设置
                existing_settings.update(settings)
                settings = existing_settings
            except json.JSONDecodeError:
                # 如果文件格式错误，则创建新的设置对象
                existing_settings = {}
                settings = existing_settings
        
        # 写入文件
        with open(overlay_file, "w", encoding="utf-8-sig") as f:
            json.dump(settings, f, ensure_ascii=False, indent=4, separators=(',', ': '))
        
        # 提示保存成功
        ModernMessageBox.success(self, "保存成功", f"自定义名称设置已成功保存到 {overlay_file}")
        self.accept()

# 彩色圆盘选择器类

class OtherOptionsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("其他选项")
        self.setFixedSize(500, 350)
        
        # 设置窗口图标（使用资源文件中的图标）
        self.setWindowIcon(QIcon(":/resource/icon.ico"))
        apply_unified_dialog_style(self)
        
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        # 标题
        title = QLabel("其他渲染选项")
        title.setObjectName("welcomeTitle")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # 背包无阴影复选框
        self.no_shadow_checkbox = QCheckBox("背包无阴影")
        self.no_shadow_checkbox.setObjectName("dragDropLabel")
        main_layout.addWidget(self.no_shadow_checkbox)
        
        # 添加垂直间距使界面更美观
        main_layout.addSpacing(40)
        
        # 底部按钮区域
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignRight)
        
        save_button = QPushButton("保存")
        save_button.setObjectName("startConversionButton")
        save_button.clicked.connect(self.save_settings)
        
        cancel_button = QPushButton("取消")
        cancel_button.setObjectName("startConversionButton")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        
        main_layout.addLayout(button_layout)
        
        # 尝试加载已保存的设置
        self.load_saved_settings()
        
    def load_saved_settings(self):
        import json
        import os
        
        # 始终使用同一个固定位置的overlay.json文件
        temp_overlay_dir = os.path.join(os.getcwd(), "temp_overlay")
        overlay_file = os.path.join(temp_overlay_dir, "overlay.json")
        
        # 如果文件不存在，不执行加载
        if not os.path.exists(overlay_file):
            return
        
        try:
            # 使用utf-8-sig编码读取文件，确保能正确解析BOM
            with open(overlay_file, "r", encoding="utf-8-sig") as f:
                settings = json.load(f)
            
            # 加载背包无阴影设置（支持旧格式'no_shadow'和新格式'core_shadow'）
            if "core_shadow" in settings:
                # 不需要取反，直接设置
                self.no_shadow_checkbox.setChecked(settings["core_shadow"].get("enabled", False))
            elif "no_shadow" in settings:
                # 向后兼容旧格式
                self.no_shadow_checkbox.setChecked(settings["no_shadow"].get("enabled", False))
        except Exception as e:
            ModernMessageBox.warning(self, "加载失败", f"加载设置时出错: {str(e)}")
        
    def save_settings(self):
        """
    保存用户在其他选项窗口中设置的选项
    """
        import json
        import os
        import datetime
        
        # 收集设置
        settings = {}
        
        # 背包无阴影设置
        settings["core_shadow"] = {
            "enabled": self.no_shadow_checkbox.isChecked()  # 不需要取反，勾选表示需要启用无阴影功能
        }
        
        # 创建temp_overlay文件夹
        temp_overlay_dir = os.path.join(os.getcwd(), "temp_overlay")
        os.makedirs(temp_overlay_dir, exist_ok=True)
        
        # 始终使用同一个固定位置的overlay.json文件
        overlay_file = os.path.join(temp_overlay_dir, "overlay.json")
        
        # 如果文件已存在，先读取现有内容
        if os.path.exists(overlay_file):
            try:
                with open(overlay_file, "r", encoding="utf-8-sig") as f:
                    existing_settings = json.load(f)
                # 合并新的设置
                existing_settings.update(settings)
                settings = existing_settings
            except json.JSONDecodeError:
                # 如果文件格式错误，则创建新的设置对象
                existing_settings = {}
                settings = existing_settings
        
        # 写入文件
        with open(overlay_file, "w", encoding="utf-8-sig") as f:
            json.dump(settings, f, ensure_ascii=False, indent=4, separators=(',', ': '))
        
        # 提示保存成功
        ModernMessageBox.success(self, "保存成功", f"其他选项已成功保存到 {overlay_file}")
        
        # 关闭对话框
        self.accept()

# 自定义物品边框颜色对话框

class BorderColorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("自定义物品边框")
        self.setFixedSize(600, 300)
        
        # 设置窗口图标（使用资源文件中的图标）
        self.setWindowIcon(QIcon(":/resource/icon.ico"))
        apply_unified_dialog_style(self)
        
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        # 标题
        title = QLabel("设置方块边框")
        title.setObjectName("welcomeTitle")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # 说明文字
        notice_label = QLabel("因为一些不知名的问题，边框颜色暂时无法使用，请等待后续开发完善")
        notice_label.setObjectName("dragDropLabel")
        notice_label.setAlignment(Qt.AlignCenter)
        notice_label.setWordWrap(True)
        main_layout.addWidget(notice_label)
        
        # 炫彩边框复选框
        self.rgb_border_checkbox = QCheckBox("炫彩边框（需显卡支持）")
        self.rgb_border_checkbox.setObjectName("dragDropLabel")
        main_layout.addWidget(self.rgb_border_checkbox, alignment=Qt.AlignCenter)
        
        # 底部按钮区域
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignRight)
        
        save_button = QPushButton("保存")
        save_button.setObjectName("startConversionButton")
        save_button.clicked.connect(self.save_settings)
        
        cancel_button = QPushButton("取消")
        cancel_button.setObjectName("startConversionButton")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        
        main_layout.addLayout(button_layout)
        
        # 加载已保存的设置
        self.load_saved_settings()
        
    # toggle_color_disc方法已移除，因为不再需要颜色选择器
        
    def load_saved_settings(self):
        """
    加载已保存的设置
    """
        import json
        import os
        
        # 从固定位置的overlay.json文件中加载设置
        temp_overlay_dir = os.path.join(os.getcwd(), "temp_overlay")
        overlay_file = os.path.join(temp_overlay_dir, "overlay.json")
        
        if os.path.exists(overlay_file):
            try:
                # 使用utf-8-sig编码读取，以支持带BOM的UTF-8文件
                with open(overlay_file, "r", encoding="utf-8-sig") as f:
                    settings = json.load(f)
                
                # 加载边框设置（支持新格式'core_outline'和'core_outline_rainbow'）
                if "core_outline_rainbow" in settings and settings["core_outline_rainbow"].get("enabled", False):
                    # 炫彩边框已启用
                    self.rgb_border_checkbox.setChecked(True)
                elif "core_outline" in settings and settings["core_outline"].get("enabled", False):
                    # 自定义颜色边框已启用 - 但我们只保留炫彩边框选项
                    self.rgb_border_checkbox.setChecked(False)
                elif "item_border" in settings:
                    # 向后兼容旧格式
                    border_settings = settings["item_border"]
                    # 检查是否选择了炫彩边框
                    if border_settings.get("type") == "rgb_border":
                        self.rgb_border_checkbox.setChecked(True)
                    else:
                        self.rgb_border_checkbox.setChecked(False)
            except Exception as e:
                print(f"加载边框设置失败: {e}")
    
    def save_settings(self):
        """
    保存用户在自定义物品边框窗口中设置的选项
    """
        import json
        import os
        
        # 收集设置
        settings = {}
        
        # 使用默认边框粗细值1
        thickness = 1
        
        # 检查是否选择了炫彩边框
        if self.rgb_border_checkbox.isChecked():
            # 炫彩边框设置为core_outline_rainbow
            settings["core_outline_rainbow"] = {
                "type": "rgb_border",
                "enabled": True,
                "name": "Rainbow Border",
                "description": "Enable GPU-accelerated colorful gradient border",
                "thickness": thickness
            }
            # 确保自定义颜色边框被禁用
            settings["core_outline"] = {
                "enabled": False
            }
        else:
            # 未选择炫彩边框时，禁用所有边框
            settings["core_outline"] = {
                "enabled": False
            }
            settings["core_outline_rainbow"] = {
                "enabled": False
            }
        
        # 创建temp_overlay文件夹
        temp_overlay_dir = os.path.join(os.getcwd(), "temp_overlay")
        os.makedirs(temp_overlay_dir, exist_ok=True)
        
        # 始终使用同一个固定位置的overlay.json文件
        overlay_file = os.path.join(temp_overlay_dir, "overlay.json")
        
        # 如果文件已存在，先读取现有内容
        if os.path.exists(overlay_file):
            try:
                with open(overlay_file, "r", encoding="utf-8-sig") as f:
                    existing_settings = json.load(f)
                # 合并新的边框设置
                existing_settings.update(settings)
                settings = existing_settings
            except json.JSONDecodeError:
                # 如果文件格式错误，则创建新的设置对象
                existing_settings = {}
                settings = existing_settings
        
        # 写入文件
        with open(overlay_file, "w", encoding="utf-8-sig") as f:
            json.dump(settings, f, ensure_ascii=False, indent=4, separators=(',', ': '))
        
        # 提示保存成功
        ModernMessageBox.success(self, "保存成功", f"边框设置已成功保存到 {overlay_file}")
        
        # 关闭对话框
        self.accept()





