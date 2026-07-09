# -*- coding: utf-8 -*-
"""
Main window for the refactored UI.
"""

from __future__ import annotations

import json
import os
import time
import webbrowser
from typing import List

import resource_rc  # noqa: F401 — needed for compiled resource loading

from PySide6.QtCore import Qt, QThread, Signal, QObject, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMenuBar,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QProgressBar,
)

from ui_components.theme import apply_main_window_styles
from ui_components.dialogs import (
    ModernMessageBox,
    ItemSizeDialog,
    BorderColorDialog,
    OtherOptionsDialog,
    CustomNameDialog,
)
from auto_updater import (
    UpdateCheckWorker,
    ReleaseInfo,
    CURRENT_VERSION,
    is_newer,
)
import pack
import overlay


class ConversionWorker(QObject):
    progress = Signal(int)
    finished = Signal(list)
    error = Signal(str)

    def __init__(self, file_paths: List[str], target_version: str, fix_alpha_layers: bool):
        super().__init__()
        self.file_paths = list(file_paths)
        self.target_version = target_version
        self.fix_alpha_layers = fix_alpha_layers

    def run(self):
        try:
            pack_format2 = pack.VERSION_TO_PACK_FORMAT_MAP.get(self.target_version)
            if pack_format2 is None:
                raise ValueError(f"不支持的目标版本：{self.target_version}")

            results, _ = pack.start_processing_conversion(
                pack_format2,
                self.progress.emit,
                self.file_paths,
                self.fix_alpha_layers,
            )
            self.finished.emit(results)
        except Exception as exc:
            self.error.emit(str(exc))


class KPTMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Kyanite Pack Tool")
        self.setMinimumSize(1200, 760)
        self.setWindowIcon(QIcon(":/resource/icon.ico"))
        self.setAcceptDrops(True)

        self.selected_files: List[str] = []
        self.parent_pack_path: str | None = None
        self.worker_thread: QThread | None = None
        self.worker: ConversionWorker | None = None
        self.conversion_start_time: float | None = None

        # update state
        self._update_thread: QThread | None = None
        self._update_worker: UpdateCheckWorker | None = None
        self._latest_release: ReleaseInfo | None = None
        self._update_checking = False

        self._build_ui()
        apply_main_window_styles(self)
        self.center_window()
        self.show_home_page()

        # 启动时自动检查更新（延迟 1 秒，避免阻塞 UI 启动）
        from PySide6.QtCore import QTimer
        QTimer.singleShot(1000, self._check_for_updates_on_startup)

    def _build_ui(self):
        root = QWidget()
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.sidebar = self._create_sidebar()
        root_layout.addWidget(self.sidebar)

        self.content_shell = QWidget()
        self.content_shell.setObjectName("contentShell")
        content_layout = QVBoxLayout(self.content_shell)
        content_layout.setContentsMargins(30, 24, 30, 24)
        content_layout.setSpacing(20)

        self.top_bar = self._create_top_bar()
        content_layout.addWidget(self.top_bar)

        self.content_area = QWidget()
        self.content_area_layout = QVBoxLayout(self.content_area)
        self.content_area_layout.setContentsMargins(0, 0, 0, 0)
        self.content_area_layout.setSpacing(0)
        content_layout.addWidget(self.content_area, 1)

        root_layout.addWidget(self.content_shell, 1)

        self.setCentralWidget(root)
        self.setMenuBar(self._create_menu_bar())

    def _create_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(240)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(18, 24, 18, 24)
        layout.setSpacing(18)

        brand = QWidget()
        brand_layout = QVBoxLayout(brand)
        brand_layout.setContentsMargins(0, 0, 0, 0)
        brand_layout.setSpacing(4)

        brand_title = QLabel("Kyanite Pack Tool")
        brand_title.setObjectName("brandTitle")
        brand_subtitle = QLabel("现代化资源包工作台")
        brand_subtitle.setObjectName("brandSubtitle")

        brand_layout.addWidget(brand_title)
        brand_layout.addWidget(brand_subtitle)

        layout.addWidget(brand)

        self.home_button = self._create_nav_button("主页")
        self.home_button.clicked.connect(self.show_home_page)

        self.convert_button = self._create_nav_button("转换")
        self.convert_button.clicked.connect(self.open_conversion_page)

        self.overlay_button = self._create_nav_button("覆盖包")
        self.overlay_button.clicked.connect(self.open_overlay_page)

        self.settings_button = self._create_nav_button("设置")
        self.settings_button.clicked.connect(self.open_settings_page)

        layout.addWidget(self.home_button)
        layout.addWidget(self.convert_button)
        layout.addWidget(self.overlay_button)
        layout.addWidget(self.settings_button)
        layout.addStretch(1)

        footer = QLabel("©2025-2026  2-Pyramid Studio")
        footer.setObjectName("brandSubtitle")
        footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer)

        return sidebar

    def _create_nav_button(self, text: str) -> QPushButton:
        button = QPushButton(text)
        button.setObjectName("navButton")
        button.setCheckable(True)
        button.setAutoExclusive(True)
        return button

    def _create_top_bar(self) -> QWidget:
        top_bar = QWidget()
        top_bar.setObjectName("topBar")
        layout = QHBoxLayout(top_bar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        self.page_title_label = QLabel("主页")
        self.page_title_label.setObjectName("pageTitle")

        layout.addWidget(self.page_title_label)
        layout.addStretch(1)

        return top_bar

    def _create_menu_bar(self) -> QMenuBar:
        menu_bar = QMenuBar(self)

        file_menu = QMenu("文件", self)
        help_menu = QMenu("帮助", self)

        menu_bar.addMenu(file_menu)
        menu_bar.addMenu(help_menu)

        return menu_bar

    def center_window(self):
        screen = self.screen() or QApplication.primaryScreen()
        if screen is None:
            return
        geometry = screen.availableGeometry()
        size = self.geometry()
        self.move(
            geometry.x() + (geometry.width() - size.width()) // 2,
            geometry.y() + (geometry.height() - size.height()) // 2,
        )

    def _fade_in(self, widget: QWidget):
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        animation = QPropertyAnimation(effect, b"opacity", widget)
        animation.setDuration(220)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.InOutQuad)
        animation.start(QPropertyAnimation.DeleteWhenStopped)

    def _switch_page(self, page_widget: QWidget, button_states: dict):
        for button, state in button_states.items():
            button.setChecked(state)

        while self.content_area_layout.count():
            item = self.content_area_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("contentScroll")
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setWidget(page_widget)

        self.content_area_layout.addWidget(scroll)
        self._fade_in(scroll)

    def create_home_page(self) -> QWidget:
        wrapper = QWidget()
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)

        hero = QFrame()
        hero.setObjectName("welcomeFrame")
        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(30, 30, 30, 30)
        hero_layout.setSpacing(10)

        title = QLabel("KyanitePackTool Code By 2-Pyramid Studio")
        title.setObjectName("welcomeTitle")
        title.setAlignment(Qt.AlignCenter)
        quick_actions = QWidget()
        quick_actions.setObjectName("quickActions")
        quick_layout = QHBoxLayout(quick_actions)
        quick_layout.setContentsMargins(0, 0, 0, 0)
        quick_layout.setSpacing(12)
        quick_layout.setAlignment(Qt.AlignCenter)

        start_convert = QPushButton("开始转换")
        start_convert.setObjectName("homeButton")
        start_convert.clicked.connect(self.open_conversion_page)

        start_overlay = QPushButton("制作覆盖包")
        start_overlay.setObjectName("homeButton")
        start_overlay.clicked.connect(self.open_overlay_page)

        open_settings = QPushButton("打开设置")
        open_settings.setObjectName("homeButton")
        open_settings.clicked.connect(self.open_settings_page)

        quick_layout.addWidget(start_convert)
        quick_layout.addWidget(start_overlay)
        quick_layout.addWidget(open_settings)

        hero_layout.addWidget(title)
        hero_layout.addWidget(quick_actions)

        layout.addWidget(hero)

        features = QFrame()
        features.setObjectName("featureGrid")
        features_layout = QVBoxLayout(features)
        features_layout.setContentsMargins(0, 0, 0, 0)
        features_layout.setSpacing(12)

        features_layout.addWidget(self._make_feature_card("跨版本转换", "支持 1.6 - 1.21.11 范围内的材质包自动转换。"))
        features_layout.addWidget(self._make_feature_card("覆盖包工作流", "可视化配置覆盖包，自定义物品大小与命名。"))
        features_layout.addWidget(self._make_feature_card("深色文本风格", "黑白基调配合细节阴影，保持清爽现代感。"))

        layout.addWidget(features)
        layout.addStretch(1)

        return wrapper

    def _make_feature_card(self, title: str, body: str) -> QFrame:
        card = QFrame()
        card.setObjectName("featureCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(6)

        title_label = QLabel(title)
        title_label.setObjectName("featureTitle")
        title_label.setAlignment(Qt.AlignCenter)
        body_label = QLabel(body)
        body_label.setObjectName("featureBody")
        body_label.setWordWrap(True)
        body_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(title_label)
        layout.addWidget(body_label)
        return card

    def show_home_page(self):
        self.page_title_label.setText("主页")
        button_states = {
            self.convert_button: False,
            self.overlay_button: False,
            self.settings_button: False,
            self.home_button: True,
        }
        self._switch_page(self.create_home_page(), button_states)

    def open_conversion_page(self):
        self.page_title_label.setText("转换")
        button_states = {
            self.convert_button: True,
            self.overlay_button: False,
            self.settings_button: False,
            self.home_button: False,
        }
        self._switch_page(self.create_conversion_page(), button_states)

    def open_overlay_page(self):
        self.page_title_label.setText("覆盖包")
        button_states = {
            self.convert_button: False,
            self.overlay_button: True,
            self.settings_button: False,
            self.home_button: False,
        }
        self._switch_page(self.create_overlay_page(), button_states)

    def open_settings_page(self):
        self.page_title_label.setText("设置")
        button_states = {
            self.convert_button: False,
            self.overlay_button: False,
            self.settings_button: True,
            self.home_button: False,
        }
        self._switch_page(self.create_settings_page(), button_states)

    def create_conversion_page(self) -> QWidget:
        wrapper = QWidget()
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        title = QLabel("转换材质包版本")
        title.setObjectName("sectionTitle")
        subtitle = QLabel("支持批量拖拽 ZIP / RAR / 文件夹，自动检测版本并转换。")
        subtitle.setObjectName("sectionSubtitle")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        drag_frame = QFrame()
        drag_frame.setObjectName("dragDropFrame")
        drag_layout = QVBoxLayout(drag_frame)
        drag_layout.setContentsMargins(24, 24, 24, 24)
        drag_layout.setSpacing(10)

        self.drag_drop_label = QLabel("将材质包拖拽到此处")
        self.drag_drop_label.setObjectName("dragDropLabel")
        self.drag_drop_label.setAlignment(Qt.AlignCenter)

        self.selection_label = QLabel("未选择任何文件")
        self.selection_label.setObjectName("dragDropLabel")
        self.selection_label.setAlignment(Qt.AlignCenter)
        self.selection_label.setWordWrap(True)

        button_row = QHBoxLayout()
        button_row.setSpacing(12)

        select_file_btn = QPushButton("选择文件")
        select_file_btn.setObjectName("selectFileButton")
        select_file_btn.clicked.connect(self.select_resource_pack)

        select_folder_btn = QPushButton("选择文件夹")
        select_folder_btn.setObjectName("selectFolderButton")
        select_folder_btn.clicked.connect(self.select_resource_folder)

        button_row.addWidget(select_file_btn)
        button_row.addWidget(select_folder_btn)
        button_row.addStretch(1)

        drag_layout.addWidget(self.drag_drop_label)
        drag_layout.addWidget(self.selection_label)
        drag_layout.addLayout(button_row)

        layout.addWidget(drag_frame)

        options_card = QFrame()
        options_card.setObjectName("conversionFrame")
        options_layout = QVBoxLayout(options_card)
        options_layout.setContentsMargins(24, 20, 24, 20)
        options_layout.setSpacing(12)

        version_row = QHBoxLayout()
        version_label = QLabel("目标版本")
        version_label.setObjectName("fieldLabel")
        self.version_combo = QComboBox()
        self.version_combo.setObjectName("versionComboBox")

        version_labels = [
            label
            for key, label in sorted(pack.PACK_FORMAT_MAP.items(), key=lambda item: item[0])
            if key != 1000  # 排除 Bedrock Latest
        ]
        self.version_combo.addItems(version_labels)

        version_row.addWidget(version_label)
        version_row.addWidget(self.version_combo, 1)

        self.fix_alpha_checkbox = QCheckBox("启用全物品贴图图层修复（Beta）")
        self.fix_alpha_checkbox.setChecked(False)

        warning_label = QLabel("注意：该功能可能显著增加转换耗时。")
        warning_label.setObjectName("warningLabel")

        options_layout.addLayout(version_row)
        options_layout.addWidget(self.fix_alpha_checkbox)
        options_layout.addWidget(warning_label)

        layout.addWidget(options_card)

        progress_card = QFrame()
        progress_card.setObjectName("conversionFrame")
        progress_layout = QVBoxLayout(progress_card)
        progress_layout.setContentsMargins(24, 20, 24, 20)
        progress_layout.setSpacing(12)

        self.status_label = QLabel("等待开始")
        self.status_label.setObjectName("fieldLabel")

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        self.start_button = QPushButton("开始转换")
        self.start_button.setObjectName("startConversionButton")
        self.start_button.clicked.connect(self.start_conversion)

        progress_layout.addWidget(self.status_label)
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.start_button)

        layout.addWidget(progress_card)
        layout.addStretch(1)

        return wrapper

    def create_overlay_page(self) -> QWidget:
        wrapper = QWidget()
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)

        title = QLabel("制作覆盖包")
        title.setObjectName("sectionTitle")
        subtitle = QLabel("快速组合设置并生成你的覆盖包。")
        subtitle.setObjectName("sectionSubtitle")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        parent_card = QFrame()
        parent_card.setObjectName("conversionFrame")
        parent_layout = QVBoxLayout(parent_card)
        parent_layout.setContentsMargins(24, 20, 24, 20)
        parent_layout.setSpacing(10)

        parent_label = QLabel("母材质包（可选）")
        parent_label.setObjectName("fieldLabel")
        parent_hint = QLabel("用于继承原包内容，未选择则从空白结构生成。")
        parent_hint.setObjectName("sectionSubtitle")
        parent_hint.setWordWrap(True)

        self.parent_pack_display = QLabel("未选择")
        self.parent_pack_display.setObjectName("sectionSubtitle")
        self.parent_pack_display.setWordWrap(True)

        parent_button_row = QHBoxLayout()
        select_parent_btn = QPushButton("选择母材质包")
        select_parent_btn.setObjectName("selectFileButton")
        select_parent_btn.clicked.connect(self.select_parent_pack)

        clear_parent_btn = QPushButton("清除选择")
        clear_parent_btn.setObjectName("optionButton")
        clear_parent_btn.clicked.connect(self.clear_parent_pack)

        parent_button_row.addWidget(select_parent_btn)
        parent_button_row.addWidget(clear_parent_btn)
        parent_button_row.addStretch(1)

        parent_layout.addWidget(parent_label)
        parent_layout.addWidget(parent_hint)
        parent_layout.addWidget(self.parent_pack_display)
        parent_layout.addLayout(parent_button_row)

        layout.addWidget(parent_card)

        option_card = QFrame()
        option_card.setObjectName("conversionFrame")
        option_layout = QVBoxLayout(option_card)
        option_layout.setContentsMargins(24, 20, 24, 20)
        option_layout.setSpacing(14)

        option_title = QLabel("覆盖包选项")
        option_title.setObjectName("fieldLabel")

        button_row = QHBoxLayout()
        button_row.setSpacing(12)

        item_size_btn = QPushButton("物品大小")
        item_size_btn.setObjectName("optionButton")
        item_size_btn.clicked.connect(self.open_item_size_dialog)

        custom_name_btn = QPushButton("自定义名称")
        custom_name_btn.setObjectName("optionButton")
        custom_name_btn.clicked.connect(self.open_custom_name_dialog)

        border_btn = QPushButton("边框设置")
        border_btn.setObjectName("optionButton")
        border_btn.clicked.connect(self.open_border_color_dialog)

        other_btn = QPushButton("其他选项")
        other_btn.setObjectName("optionButton")
        other_btn.clicked.connect(self.open_other_options_dialog)

        button_row.addWidget(item_size_btn)
        button_row.addWidget(custom_name_btn)
        button_row.addWidget(border_btn)
        button_row.addWidget(other_btn)

        option_layout.addWidget(option_title)
        option_layout.addLayout(button_row)

        layout.addWidget(option_card)

        generate_card = QFrame()
        generate_card.setObjectName("conversionFrame")
        generate_layout = QVBoxLayout(generate_card)
        generate_layout.setContentsMargins(24, 20, 24, 20)
        generate_layout.setSpacing(12)

        generate_label = QLabel("生成覆盖包")
        generate_label.setObjectName("fieldLabel")
        generate_hint = QLabel("确认设置后点击生成按钮。")
        generate_hint.setObjectName("sectionSubtitle")

        generate_button = QPushButton("开始生成")
        generate_button.setObjectName("startConversionButton")
        generate_button.clicked.connect(self.generate_overlay_pack)

        generate_layout.addWidget(generate_label)
        generate_layout.addWidget(generate_hint)
        generate_layout.addWidget(generate_button)

        layout.addWidget(generate_card)
        layout.addStretch(1)

        return wrapper

    def create_settings_page(self) -> QWidget:
        wrapper = QWidget()
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        title = QLabel("应用设置")
        title.setObjectName("sectionTitle")
        title.setAlignment(Qt.AlignCenter)
        subtitle = QLabel("查看当前版本信息与运行环境。")
        subtitle.setObjectName("sectionSubtitle")
        subtitle.setAlignment(Qt.AlignCenter)

        layout.addWidget(title)
        layout.addWidget(subtitle)

        # ── 版本信息卡片 ──
        info_card = QFrame()
        info_card.setObjectName("conversionFrame")
        info_layout = QVBoxLayout(info_card)
        info_layout.setContentsMargins(24, 20, 24, 20)
        info_layout.setSpacing(10)

        version_label = QLabel(f"当前版本：{CURRENT_VERSION}")
        version_label.setObjectName("fieldLabel")
        version_label.setAlignment(Qt.AlignCenter)

        team_label = QLabel("开发团队：2-Pyramid Studio")
        team_label.setObjectName("fieldLabel")
        team_label.setAlignment(Qt.AlignCenter)

        python_label = QLabel(f"Python：{platform_version()}")
        python_label.setObjectName("sectionSubtitle")
        python_label.setAlignment(Qt.AlignCenter)

        info_layout.addWidget(version_label)
        info_layout.addWidget(team_label)
        info_layout.addWidget(python_label)

        # ── 更新状态 ──
        self._update_status_label = QLabel("启动时自动检查更新…")
        self._update_status_label.setObjectName("sectionSubtitle")
        self._update_status_label.setAlignment(Qt.AlignCenter)
        self._update_status_label.setWordWrap(True)
        info_layout.addWidget(self._update_status_label)

        update_button = QPushButton("检查更新")
        update_button.setObjectName("homeButton")
        update_button.setFixedWidth(160)
        update_button.clicked.connect(self._start_update_check)
        # center the button
        update_btn_layout = QHBoxLayout()
        update_btn_layout.setAlignment(Qt.AlignCenter)
        update_btn_layout.addWidget(update_button)
        info_layout.addLayout(update_btn_layout)

        layout.addWidget(info_card)

        # ── 联系方式卡片 ──
        contact_card = QFrame()
        contact_card.setObjectName("conversionFrame")
        contact_layout = QVBoxLayout(contact_card)
        contact_layout.setContentsMargins(24, 20, 24, 20)
        contact_layout.setSpacing(10)

        contact_title = QLabel("联系方式")
        contact_title.setObjectName("sectionTitle")
        contact_title.setAlignment(Qt.AlignCenter)
        contact_layout.addWidget(contact_title)

        contact_buttons = QHBoxLayout()
        contact_buttons.setSpacing(12)
        contact_buttons.setAlignment(Qt.AlignCenter)

        bilibili_btn = QPushButton("Bilibili")
        bilibili_btn.setObjectName("homeButton")
        bilibili_btn.clicked.connect(lambda: self.show_contact_info("bilibili"))

        afdian_btn = QPushButton("爱发电")
        afdian_btn.setObjectName("homeButton")
        afdian_btn.clicked.connect(lambda: self.show_contact_info("afdian"))

        github_btn = QPushButton("GitHub")
        github_btn.setObjectName("homeButton")
        github_btn.clicked.connect(lambda: self.show_contact_info("github"))

        contact_buttons.addWidget(bilibili_btn)
        contact_buttons.addWidget(afdian_btn)
        contact_buttons.addWidget(github_btn)
        contact_layout.addLayout(contact_buttons)

        layout.addWidget(contact_card)

        settings_footer = QLabel("©2025-2026 2-Pyramid Studio")
        settings_footer.setObjectName("sectionSubtitle")
        settings_footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(settings_footer)

        layout.addStretch(1)

        return wrapper

    # ── 自动更新 ──────────────────────────────────────────

    def _check_for_updates_on_startup(self):
        """启动时静默检查更新。"""
        self._run_update_check(silent=True)

    def _start_update_check(self):
        """用户手动点击"检查更新"。"""
        if self._update_checking:
            return
        self._update_status_label.setText("正在检查更新…")
        self._run_update_check(silent=False)

    def _run_update_check(self, silent: bool = False):
        """在后台线程中运行更新检查。"""
        if self._update_checking:
            return
        self._update_checking = True

        self._update_thread = QThread(self)
        self._update_worker = UpdateCheckWorker()
        self._update_worker.moveToThread(self._update_thread)

        self._update_thread.started.connect(self._update_worker.run)
        self._update_worker.finished.connect(
            lambda release: self._on_update_check_finished(release, silent)
        )
        self._update_worker.error.connect(
            lambda err: self._on_update_check_error(err, silent)
        )

        # cleanup
        self._update_worker.finished.connect(self._update_thread.quit)
        self._update_worker.error.connect(self._update_thread.quit)
        self._update_worker.finished.connect(self._update_worker.deleteLater)
        self._update_worker.error.connect(self._update_worker.deleteLater)
        self._update_thread.finished.connect(self._update_thread.deleteLater)

        def cleanup_refs():
            self._update_thread = None
            self._update_worker = None
            self._update_checking = False

        self._update_thread.finished.connect(cleanup_refs)
        self._update_thread.start()

    def _on_update_check_finished(self, release: ReleaseInfo | None, silent: bool):
        if release is None:
            self._update_status_label.setText("当前已是最新版本。")
            if not silent:
                ModernMessageBox.success(self, "检查更新", "您已使用最新版本！")
            return

        self._latest_release = release

        if is_newer(release.version, CURRENT_VERSION):
            status = f"发现新版本：{release.tag_name}（当前 {CURRENT_VERSION}）"
            self._update_status_label.setText(status)
            if not silent:
                self._show_update_dialog(release)
        else:
            self._update_status_label.setText(f"当前已是最新版本（{CURRENT_VERSION}）")
            if not silent:
                ModernMessageBox.success(self, "检查更新", "您已使用最新版本！")

    def _on_update_check_error(self, error_msg: str, silent: bool):
        self._update_status_label.setText(f"检查更新失败：{error_msg}")
        if not silent:
            ModernMessageBox.warning(self, "检查更新失败", f"无法连接到 GitHub：{error_msg}")

    def _show_update_dialog(self, release: ReleaseInfo):
        """显示新版本提示对话框。"""
        body_preview = release.body[:300] + "…" if len(release.body) > 300 else release.body
        message = (
            f"<b>发现新版本：{release.tag_name}</b><br><br>"
            f"当前版本：{CURRENT_VERSION}<br>"
            f"最新版本：{release.version}<br><br>"
            f"<b>更新内容：</b><br>{body_preview}<br><br>"
            f"前往 GitHub 下载？"
        )
        result = ModernMessageBox.question(self, "发现新版本", message)
        if result:
            webbrowser.open(release.html_url)

    # ── 版本信息 ────────────────────────────────────────

    def read_app_version(self) -> str:
        return CURRENT_VERSION

    def open_item_size_dialog(self):
        dialog = ItemSizeDialog(self)
        dialog.exec()

    def open_custom_name_dialog(self):
        dialog = CustomNameDialog(self)
        dialog.exec()

    def open_border_color_dialog(self):
        dialog = BorderColorDialog(self)
        dialog.exec()

    def open_other_options_dialog(self):
        dialog = OtherOptionsDialog(self)
        dialog.exec()

    def show_contact_info(self, platform):
        """显示不同平台的联系方式"""
        contacts = {
            "bilibili": "B站主页：https://space.bilibili.com/3493094785812897?spm_id_from=333.1007.0.0",
            "afdian": "爱发电支持：https://afdian.com/a/asHurricane",
            "github": "GitHub仓库：https://github.com/realLivedInCorner/2-Pyramid"
        }

        if platform in contacts:
            ModernMessageBox.info(self, "联系方式", contacts[platform])

    def select_resource_pack(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "选择材质包文件",
            "",
            "资源包文件 (*.zip *.rar *.7z *.tar *.gz *.bz2);;所有文件 (*.*)",
        )
        if file_paths:
            self.selected_files = list(file_paths)
            self._update_selection_label()

    def select_resource_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "选择材质包文件夹", "")
        if folder_path:
            self.selected_files = [folder_path]
            self._update_selection_label()

    def _update_selection_label(self):
        if not hasattr(self, "selection_label"):
            return
        if not self.selected_files:
            self.selection_label.setText("未选择任何文件")
            return
        if len(self.selected_files) == 1:
            self.selection_label.setText(self.selected_files[0])
        else:
            self.selection_label.setText(f"已选择 {len(self.selected_files)} 个文件")

    def select_parent_pack(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择母材质包",
            "",
            "资源包文件 (*.zip *.rar *.7z);;所有文件 (*.*)",
        )
        if file_path:
            self.parent_pack_path = file_path
            self.parent_pack_display.setText(file_path)
            self._save_parent_pack_setting(file_path)

    def clear_parent_pack(self):
        self.parent_pack_path = None
        self.parent_pack_display.setText("未选择")
        self._save_parent_pack_setting("")

    def _save_parent_pack_setting(self, path: str):
        temp_overlay_dir = os.path.join(os.getcwd(), "temp_overlay")
        os.makedirs(temp_overlay_dir, exist_ok=True)
        overlay_file = os.path.join(temp_overlay_dir, "overlay.json")

        settings = {}
        if os.path.exists(overlay_file):
            try:
                with open(overlay_file, "r", encoding="utf-8-sig") as f:
                    settings = json.load(f)
            except Exception:
                settings = {}

        if path:
            settings["parent_pack"] = {"enabled": True, "path": path}
        else:
            settings["parent_pack"] = {"enabled": False, "path": ""}

        with open(overlay_file, "w", encoding="utf-8-sig") as f:
            json.dump(settings, f, ensure_ascii=False, indent=4, separators=(',', ': '))

    def generate_overlay_pack(self):
        try:
            overlay.start_overlay()
            output_path = overlay.package_overlay_resource_pack()
            if output_path:
                ModernMessageBox.success(self, "生成完成", f"覆盖包已生成：{output_path}")
            else:
                ModernMessageBox.warning(self, "生成失败", "未能生成覆盖包，请检查设置。")
        except Exception as exc:
            ModernMessageBox.error(self, "生成失败", str(exc))

    def start_conversion(self):
        if not self.selected_files:
            ModernMessageBox.warning(self, "提示", "请先选择材质包文件或文件夹。")
            return

        # 如果线程已经存在且正在运行，则提示用户
        if self.worker_thread and self.worker_thread.isRunning():
            ModernMessageBox.warning(self, "提示", "当前转换任务尚未结束，请稍候。")
            return

        # 确保之前的线程资源被清理
        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait()
            self.worker_thread = None

        target_version = self.version_combo.currentText()
        fix_alpha_layers = self.fix_alpha_checkbox.isChecked()
        self.status_label.setText("转换中，请稍候...")
        self.conversion_start_time = time.time()
        self.progress_bar.setValue(0)
        self.start_button.setEnabled(False)

        self.worker_thread = QThread(self)
        self.worker = ConversionWorker(self.selected_files, target_version, fix_alpha_layers)
        self.worker.moveToThread(self.worker_thread)

        self.worker_thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.conversion_finished)
        self.worker.error.connect(self.conversion_error)
        
        # 确保资源在完成后被清理
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.error.connect(self.worker_thread.quit)
        self.worker.error.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        
        # 完成后重置引用，确保下一次转换可以正常开始
        def cleanup():
            self.worker_thread = None
            self.worker = None
            
        self.worker_thread.finished.connect(cleanup)

        self.worker_thread.start()

    def update_progress(self, value: int):
        value = max(0, min(100, int(value)))
        self.progress_bar.setValue(value)

    def conversion_finished(self, results: list):
        self.start_button.setEnabled(True)
        self.progress_bar.setValue(100)

        elapsed_text = ""
        if self.conversion_start_time is not None:
            elapsed_seconds = max(0.0, time.time() - self.conversion_start_time)
            elapsed_text = f"\n总用时：{elapsed_seconds:.2f} 秒"

        self.status_label.setText(f"转换完成{elapsed_text}")

        if results:
            ModernMessageBox.success(self, "转换完成", f"成功转换 {len(results)} 个文件。{elapsed_text}")
        else:
            ModernMessageBox.warning(self, "转换完成", f"没有生成任何输出文件。{elapsed_text}")

    def conversion_error(self, message: str):
        self.start_button.setEnabled(True)
        self.progress_bar.setValue(0)

        elapsed_text = ""
        if self.conversion_start_time is not None:
            elapsed_seconds = max(0.0, time.time() - self.conversion_start_time)
            elapsed_text = f"\n总用时：{elapsed_seconds:.2f} 秒"

        self.status_label.setText(f"转换失败{elapsed_text}")
        ModernMessageBox.error(self, "转换失败", f"{message}{elapsed_text}")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if not urls:
            return

        paths = [url.toLocalFile() for url in urls if url.isLocalFile()]
        if not paths:
            return

        self.selected_files = paths
        self._update_selection_label()


def platform_version() -> str:
    import sys
    return sys.version.split(" ")[0]