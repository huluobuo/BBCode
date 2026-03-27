# -*- coding: utf-8 -*-
"""
BBCode PyQt6 主题系统
基于 QSS (Qt StyleSheet) 的现代主题管理
"""

from typing import Dict, Optional, Callable
from dataclasses import dataclass
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor, QFont
from PyQt6.QtCore import Qt


@dataclass
class ThemeColors:
    """主题颜色配置"""
    # 背景色
    bg_primary: str = "#1e1e1e"
    bg_secondary: str = "#252526"
    bg_tertiary: str = "#2d2d30"
    bg_hover: str = "#3e3e42"
    
    # 文本色
    text_primary: str = "#cccccc"
    text_secondary: str = "#858585"
    text_disabled: str = "#656565"
    
    # 强调色
    accent: str = "#007acc"
    accent_hover: str = "#0098ff"
    accent_pressed: str = "#005a9e"
    
    # 边框
    border: str = "#3e3e42"
    border_focus: str = "#007acc"
    
    # 状态色
    success: str = "#4ec9b0"
    warning: str = "#ce9178"
    error: str = "#f44747"
    info: str = "#75beff"
    
    # 语法高亮色
    keyword: str = "#569cd6"
    string: str = "#ce9178"
    comment: str = "#6a9955"
    function: str = "#dcdcaa"
    number: str = "#b5cea8"
    operator: str = "#d4d4d4"


class ThemeManager:
    """主题管理器"""
    
    _instance: Optional['ThemeManager'] = None
    _current_theme: str = "dark"
    _colors: ThemeColors = ThemeColors()
    _change_listeners: list = []
    
    # 预定义主题
    THEMES = {
        "dark": ThemeColors(
            bg_primary="#1e1e1e",
            bg_secondary="#252526",
            bg_tertiary="#2d2d30",
            bg_hover="#3e3e42",
            text_primary="#cccccc",
            text_secondary="#858585",
            text_disabled="#656565",
            accent="#007acc",
            accent_hover="#0098ff",
            accent_pressed="#005a9e",
            border="#3e3e42",
            border_focus="#007acc",
            success="#4ec9b0",
            warning="#ce9178",
            error="#f44747",
            info="#75beff",
            keyword="#569cd6",
            string="#ce9178",
            comment="#6a9955",
            function="#dcdcaa",
            number="#b5cea8",
            operator="#d4d4d4",
        ),
        "light": ThemeColors(
            bg_primary="#ffffff",
            bg_secondary="#f3f3f3",
            bg_tertiary="#e8e8e8",
            bg_hover="#d4d4d4",
            text_primary="#323130",
            text_secondary="#605e5c",
            text_disabled="#a19f9d",
            accent="#0078d4",
            accent_hover="#106ebe",
            accent_pressed="#005a9e",
            border="#e0e0e0",
            border_focus="#0078d4",
            success="#107c10",
            warning="#ffc107",
            error="#d13438",
            info="#0078d4",
            keyword="#0000ff",
            string="#a31515",
            comment="#008000",
            function="#795e26",
            number="#098658",
            operator="#000000",
        ),
        "glass_dark": ThemeColors(
            bg_primary="#0d1117",
            bg_secondary="#161b22",
            bg_tertiary="#21262d",
            bg_hover="#30363d",
            text_primary="#c9d1d9",
            text_secondary="#8b949e",
            text_disabled="#6e7681",
            accent="#58a6ff",
            accent_hover="#79c0ff",
            accent_pressed="#1f6feb",
            border="#30363d",
            border_focus="#58a6ff",
            success="#3fb950",
            warning="#d29922",
            error="#f85149",
            info="#58a6ff",
            keyword="#ff7b72",
            string="#a5d6ff",
            comment="#8b949e",
            function="#d2a8ff",
            number="#79c0ff",
            operator="#ff7b72",
        ),
        "clean_light": ThemeColors(
            bg_primary="#fafafa",
            bg_secondary="#f0f0f0",
            bg_tertiary="#e8e8e8",
            bg_hover="#e0e0e0",
            text_primary="#2c2c2c",
            text_secondary="#666666",
            text_disabled="#999999",
            accent="#2196f3",
            accent_hover="#42a5f5",
            accent_pressed="#1976d2",
            border="#e0e0e0",
            border_focus="#2196f3",
            success="#4caf50",
            warning="#ff9800",
            error="#f44336",
            info="#2196f3",
            keyword="#1976d2",
            string="#d32f2f",
            comment="#388e3c",
            function="#7b1fa2",
            number="#00796b",
            operator="#424242",
        ),
    }
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def get_instance(cls) -> 'ThemeManager':
        """获取主题管理器单例"""
        if cls._instance is None:
            cls._instance = ThemeManager()
        return cls._instance
    
    def set_theme(self, theme_name: str) -> None:
        """设置当前主题"""
        if theme_name in self.THEMES:
            self._current_theme = theme_name
            self._colors = self.THEMES[theme_name]
            self._notify_change()
    
    def get_theme(self) -> str:
        """获取当前主题名称"""
        return self._current_theme
    
    def get_colors(self) -> ThemeColors:
        """获取当前主题颜色"""
        return self._colors
    
    def get_color(self, color_name: str) -> str:
        """获取特定颜色值"""
        return getattr(self._colors, color_name, "#000000")
    
    def add_change_listener(self, callback: Callable):
        """添加主题变更监听器"""
        self._change_listeners.append(callback)
    
    def remove_change_listener(self, callback: Callable):
        """移除主题变更监听器"""
        if callback in self._change_listeners:
            self._change_listeners.remove(callback)
    
    def _notify_change(self):
        """通知所有监听器主题已变更"""
        for callback in self._change_listeners:
            try:
                callback(self._current_theme, self._colors)
            except Exception:
                pass
    
    def get_available_themes(self) -> list:
        """获取所有可用主题列表"""
        return list(self.THEMES.keys())
    
    def apply_to_application(self, app: QApplication) -> None:
        """应用主题到 Qt 应用程序"""
        app.setStyle('Fusion')
        
        # 设置调色板
        palette = QPalette()
        colors = self._colors
        
        palette.setColor(QPalette.ColorRole.Window, QColor(colors.bg_primary))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(colors.text_primary))
        palette.setColor(QPalette.ColorRole.Base, QColor(colors.bg_secondary))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(colors.bg_tertiary))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(colors.bg_primary))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(colors.text_primary))
        palette.setColor(QPalette.ColorRole.Text, QColor(colors.text_primary))
        palette.setColor(QPalette.ColorRole.Button, QColor(colors.bg_tertiary))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(colors.text_primary))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(colors.accent))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(colors.accent))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
        
        app.setPalette(palette)
        
        # 应用 QSS 样式表
        app.setStyleSheet(self.get_stylesheet())
    
    def get_stylesheet(self) -> str:
        """获取 QSS 样式表"""
        c = self._colors
        
        return f"""
        /* ==================== 全局样式 ==================== */
        QWidget {{
            font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
            font-size: 13px;
        }}
        
        /* ==================== 主窗口 ==================== */
        QMainWindow {{
            background-color: {c.bg_primary};
        }}
        
        /* ==================== 菜单栏 ==================== */
        QMenuBar {{
            background-color: {c.bg_secondary};
            color: {c.text_primary};
            border-bottom: 1px solid {c.border};
            padding: 2px;
        }}
        
        QMenuBar::item {{
            background-color: transparent;
            padding: 6px 12px;
            border-radius: 4px;
            margin: 2px;
        }}
        
        QMenuBar::item:selected {{
            background-color: {c.accent};
            color: white;
        }}
        
        QMenuBar::item:pressed {{
            background-color: {c.accent_pressed};
        }}
        
        /* ==================== 菜单 ==================== */
        QMenu {{
            background-color: {c.bg_secondary};
            color: {c.text_primary};
            border: 1px solid {c.border};
            padding: 4px;
            border-radius: 6px;
        }}
        
        QMenu::item {{
            padding: 6px 24px;
            border-radius: 4px;
        }}
        
        QMenu::item:selected {{
            background-color: {c.accent};
            color: white;
        }}
        
        QMenu::separator {{
            height: 1px;
            background-color: {c.border};
            margin: 4px 8px;
        }}
        
        QMenu::icon {{
            padding-left: 8px;
        }}
        
        /* ==================== 工具栏 ==================== */
        QToolBar {{
            background-color: {c.bg_secondary};
            border-bottom: 1px solid {c.border};
            spacing: 4px;
            padding: 4px;
        }}
        
        QToolButton {{
            background-color: transparent;
            border: none;
            padding: 6px 10px;
            border-radius: 4px;
            color: {c.text_primary};
        }}
        
        QToolButton:hover {{
            background-color: {c.bg_hover};
        }}
        
        QToolButton:pressed {{
            background-color: {c.accent};
            color: white;
        }}
        
        QToolButton:checked {{
            background-color: {c.accent};
            color: white;
        }}
        
        /* ==================== 标签页 ==================== */
        QTabWidget::pane {{
            border: 1px solid {c.border};
            background-color: {c.bg_primary};
            border-radius: 4px;
        }}
        
        QTabBar::tab {{
            background-color: {c.bg_secondary};
            color: {c.text_secondary};
            padding: 8px 16px;
            border: none;
            border-bottom: 2px solid transparent;
            margin-right: 2px;
            border-radius: 4px 4px 0 0;
        }}
        
        QTabBar::tab:selected {{
            background-color: {c.bg_primary};
            color: {c.text_primary};
            border-bottom: 2px solid {c.accent};
        }}
        
        QTabBar::tab:hover:!selected {{
            background-color: {c.bg_hover};
            color: {c.text_primary};
        }}
        
        QTabBar::close-button {{
            image: none;
            subcontrol-position: right;
            width: 16px;
            height: 16px;
            margin-left: 4px;
            border-radius: 3px;
            background-color: transparent;
        }}
        
        QTabBar::close-button::hover {{
            background-color: {c.error};
            color: white;
        }}
        
        QTabBar::tab:hover QTabBar::close-button {{
            background-color: {c.bg_hover};
        }}
        
        QTabBar::tab:hover QTabBar::close-button:hover {{
            background-color: {c.error};
        }}
        
        /* ==================== 文本编辑器 ==================== */
        QTextEdit, QPlainTextEdit {{
            background-color: {c.bg_secondary};
            color: {c.text_primary};
            border: 1px solid {c.border};
            border-radius: 4px;
            padding: 8px;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 13px;
            selection-background-color: {c.accent};
            selection-color: white;
        }}
        
        QTextEdit:focus, QPlainTextEdit:focus {{
            border: 1px solid {c.border_focus};
        }}
        
        /* ==================== 树形视图 ==================== */
        QTreeView {{
            background-color: {c.bg_secondary};
            color: {c.text_primary};
            border: 1px solid {c.border};
            outline: none;
            border-radius: 4px;
        }}
        
        QTreeView::item {{
            padding: 4px 8px;
            border-radius: 4px;
        }}
        
        QTreeView::item:selected {{
            background-color: {c.accent};
            color: white;
        }}
        
        QTreeView::item:hover:!selected {{
            background-color: {c.bg_hover};
        }}
        
        QTreeView::branch {{
            background-color: transparent;
        }}
        
        QTreeView::branch:has-children:!has-siblings:closed,
        QTreeView::branch:closed:has-children:has-siblings {{
            border-image: none;
            image: url(:/icons/branch-closed.png);
        }}
        
        QTreeView::branch:open:has-children:!has-siblings,
        QTreeView::branch:open:has-children:has-siblings {{
            border-image: none;
            image: url(:/icons/branch-open.png);
        }}
        
        /* ==================== 按钮 ==================== */
        QPushButton {{
            background-color: {c.bg_tertiary};
            color: {c.text_primary};
            border: 1px solid {c.border};
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: 500;
        }}
        
        QPushButton:hover {{
            background-color: {c.bg_hover};
            border-color: {c.accent};
        }}
        
        QPushButton:pressed {{
            background-color: {c.accent};
            color: white;
            border-color: {c.accent};
        }}
        
        QPushButton:disabled {{
            background-color: {c.bg_secondary};
            color: {c.text_disabled};
            border-color: {c.border};
        }}
        
        QPushButton#primary {{
            background-color: {c.accent};
            color: white;
            border-color: {c.accent};
        }}
        
        QPushButton#primary:hover {{
            background-color: {c.accent_hover};
            border-color: {c.accent_hover};
        }}
        
        QPushButton#success {{
            background-color: {c.success};
            color: white;
            border-color: {c.success};
        }}
        
        QPushButton#danger {{
            background-color: {c.error};
            color: white;
            border-color: {c.error};
        }}
        
        /* ==================== 输入框 ==================== */
        QLineEdit {{
            background-color: {c.bg_secondary};
            color: {c.text_primary};
            border: 1px solid {c.border};
            border-radius: 4px;
            padding: 8px;
        }}
        
        QLineEdit:focus {{
            border: 1px solid {c.border_focus};
        }}
        
        QLineEdit:disabled {{
            background-color: {c.bg_tertiary};
            color: {c.text_disabled};
        }}
        
        /* ==================== 下拉框 ==================== */
        QComboBox {{
            background-color: {c.bg_secondary};
            color: {c.text_primary};
            border: 1px solid {c.border};
            border-radius: 4px;
            padding: 8px;
            min-width: 100px;
        }}
        
        QComboBox:hover {{
            border: 1px solid {c.accent};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 24px;
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 6px solid {c.text_secondary};
            width: 0;
            height: 0;
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {c.bg_secondary};
            color: {c.text_primary};
            border: 1px solid {c.border};
            selection-background-color: {c.accent};
            selection-color: white;
            border-radius: 4px;
        }}
        
        /* ==================== 状态栏 ==================== */
        QStatusBar {{
            background-color: {c.bg_secondary};
            color: {c.text_secondary};
            border-top: 1px solid {c.border};
        }}
        
        QStatusBar::item {{
            border: none;
        }}
        
        /* ==================== 进度条 ==================== */
        QProgressBar {{
            border: none;
            background-color: {c.bg_tertiary};
            border-radius: 3px;
            height: 6px;
            text-align: center;
        }}
        
        QProgressBar::chunk {{
            background-color: {c.accent};
            border-radius: 3px;
        }}
        
        /* ==================== 分割器 ==================== */
        QSplitter::handle {{
            background-color: {c.border};
        }}
        
        QSplitter::handle:horizontal {{
            width: 2px;
        }}
        
        QSplitter::handle:vertical {{
            height: 2px;
        }}
        
        QSplitter::handle:hover {{
            background-color: {c.accent};
        }}
        
        /* ==================== 停靠窗口 ==================== */
        QDockWidget {{
            titlebar-close-icon: url(:/icons/close.png);
            titlebar-normal-icon: url(:/icons/float.png);
        }}
        
        QDockWidget::title {{
            background-color: {c.bg_secondary};
            padding: 8px;
            border: 1px solid {c.border};
            border-radius: 4px 4px 0 0;
        }}
        
        QDockWidget::close-button, QDockWidget::float-button {{
            background-color: transparent;
            border-radius: 2px;
            padding: 2px;
        }}
        
        QDockWidget::close-button:hover, QDockWidget::float-button:hover {{
            background-color: {c.bg_hover};
        }}
        
        /* ==================== 滚动条 ==================== */
        QScrollBar:vertical {{
            background-color: {c.bg_secondary};
            width: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {c.border};
            border-radius: 6px;
            min-height: 30px;
            margin: 2px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {c.text_secondary};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        
        QScrollBar:horizontal {{
            background-color: {c.bg_secondary};
            height: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: {c.border};
            border-radius: 6px;
            min-width: 30px;
            margin: 2px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: {c.text_secondary};
        }}
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}
        
        /* ==================== 列表视图 ==================== */
        QListView {{
            background-color: {c.bg_secondary};
            color: {c.text_primary};
            border: 1px solid {c.border};
            border-radius: 4px;
            outline: none;
        }}
        
        QListView::item {{
            padding: 6px 12px;
            border-radius: 4px;
        }}
        
        QListView::item:selected {{
            background-color: {c.accent};
            color: white;
        }}
        
        QListView::item:hover:!selected {{
            background-color: {c.bg_hover};
        }}
        
        /* ==================== 表格视图 ==================== */
        QTableView {{
            background-color: {c.bg_secondary};
            color: {c.text_primary};
            border: 1px solid {c.border};
            gridline-color: {c.border};
            outline: none;
            border-radius: 4px;
        }}
        
        QTableView::item {{
            padding: 6px;
        }}
        
        QTableView::item:selected {{
            background-color: {c.accent};
            color: white;
        }}
        
        QHeaderView::section {{
            background-color: {c.bg_tertiary};
            color: {c.text_primary};
            padding: 8px;
            border: none;
            border-right: 1px solid {c.border};
            border-bottom: 1px solid {c.border};
        }}
        
        QHeaderView::section:hover {{
            background-color: {c.bg_hover};
        }}
        
        /* ==================== 分组框 ==================== */
        QGroupBox {{
            background-color: {c.bg_secondary};
            color: {c.text_primary};
            border: 1px solid {c.border};
            border-radius: 4px;
            margin-top: 12px;
            padding-top: 12px;
            font-weight: bold;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 8px;
        }}
        
        /* ==================== 复选框 ==================== */
        QCheckBox {{
            color: {c.text_primary};
            spacing: 8px;
        }}
        
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border: 1px solid {c.border};
            border-radius: 3px;
            background-color: {c.bg_secondary};
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {c.accent};
            border-color: {c.accent};
        }}
        
        QCheckBox::indicator:hover {{
            border-color: {c.accent};
        }}
        
        /* ==================== 单选框 ==================== */
        QRadioButton {{
            color: {c.text_primary};
            spacing: 8px;
        }}
        
        QRadioButton::indicator {{
            width: 18px;
            height: 18px;
            border: 1px solid {c.border};
            border-radius: 9px;
            background-color: {c.bg_secondary};
        }}
        
        QRadioButton::indicator:checked {{
            background-color: {c.accent};
            border-color: {c.accent};
        }}
        
        QRadioButton::indicator:hover {{
            border-color: {c.accent};
        }}
        
        /* ==================== 滑块 ==================== */
        QSlider::groove:horizontal {{
            height: 4px;
            background-color: {c.bg_tertiary};
            border-radius: 2px;
        }}
        
        QSlider::handle:horizontal {{
            width: 16px;
            height: 16px;
            background-color: {c.accent};
            border-radius: 8px;
            margin: -6px 0;
        }}
        
        QSlider::handle:horizontal:hover {{
            background-color: {c.accent_hover};
        }}
        
        QSlider::sub-page:horizontal {{
            background-color: {c.accent};
            border-radius: 2px;
        }}
        
        /* ==================== 微调框 ==================== */
        QSpinBox, QDoubleSpinBox {{
            background-color: {c.bg_secondary};
            color: {c.text_primary};
            border: 1px solid {c.border};
            border-radius: 4px;
            padding: 8px;
        }}
        
        QSpinBox:focus, QDoubleSpinBox:focus {{
            border: 1px solid {c.border_focus};
        }}
        
        QSpinBox::up-button, QDoubleSpinBox::up-button,
        QSpinBox::down-button, QDoubleSpinBox::down-button {{
            background-color: {c.bg_tertiary};
            border: none;
            width: 20px;
        }}
        
        QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
        QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
            background-color: {c.bg_hover};
        }}
        
        /* ==================== 对话框 ==================== */
        QDialog {{
            background-color: {c.bg_primary};
        }}
        
        QMessageBox {{
            background-color: {c.bg_primary};
        }}
        
        /* ==================== 标签 ==================== */
        QLabel {{
            color: {c.text_primary};
        }}
        
        QLabel#heading {{
            font-size: 18px;
            font-weight: bold;
            color: {c.text_primary};
        }}
        
        QLabel#subheading {{
            font-size: 14px;
            color: {c.text_secondary};
        }}
        
        /* ==================== 工具提示 ==================== */
        QToolTip {{
            background-color: {c.bg_secondary};
            color: {c.text_primary};
            border: 1px solid {c.border};
            padding: 6px 10px;
            border-radius: 4px;
        }}
        """


# 全局主题管理器实例
theme_manager = ThemeManager.get_instance()


def get_theme_manager() -> ThemeManager:
    """获取全局主题管理器"""
    return theme_manager


def apply_theme(app: QApplication, theme_name: str = "dark") -> None:
    """便捷函数：应用主题到应用程序"""
    manager = get_theme_manager()
    manager.set_theme(theme_name)
    manager.apply_to_application(app)
