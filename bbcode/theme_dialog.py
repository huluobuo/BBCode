# -*- coding: utf-8 -*-
"""
BBCode 主题选择对话框
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QRadioButton, QButtonGroup, QFrame, QScrollArea, QWidget,
    QGridLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class ThemeDialog(QDialog):
    """主题选择对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择主题")
        self.setMinimumSize(400, 350)
        
        self._selected_theme = "Modern Dark"
        self._is_dark = True
        
        self._setup_ui()
        self._load_current_theme()
    
    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title = QLabel("选择主题")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # 创建滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        # 内容容器
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(15)
        
        # 浅色主题组
        light_group = QFrame()
        light_group.setFrameStyle(QFrame.Shape.StyledPanel)
        light_layout = QVBoxLayout(light_group)
        light_layout.setContentsMargins(15, 15, 15, 15)
        light_layout.setSpacing(10)
        
        light_title = QLabel("浅色主题")
        light_title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        light_layout.addWidget(light_title)
        
        self.light_buttons = QButtonGroup(self)
        light_themes = [
            ("Modern Light", "现代浅色"),
            ("Ocean Breeze", "海洋微风"),
            ("Forest Calm", "森林宁静"),
            ("Sunset Warm", "日落温暖"),
        ]
        for theme_name, display_name in light_themes:
            radio = QRadioButton(f"{theme_name} - {display_name}")
            radio.setProperty('theme_name', theme_name)
            radio.setProperty('is_dark', False)
            self.light_buttons.addButton(radio)
            light_layout.addWidget(radio)
        
        content_layout.addWidget(light_group)
        
        # 深色主题组
        dark_group = QFrame()
        dark_group.setFrameStyle(QFrame.Shape.StyledPanel)
        dark_layout = QVBoxLayout(dark_group)
        dark_layout.setContentsMargins(15, 15, 15, 15)
        dark_layout.setSpacing(10)
        
        dark_title = QLabel("深色主题")
        dark_title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        dark_layout.addWidget(dark_title)
        
        self.dark_buttons = QButtonGroup(self)
        dark_themes = [
            ("Modern Dark", "现代深色"),
            ("Midnight Purple", "午夜紫"),
        ]
        for theme_name, display_name in dark_themes:
            radio = QRadioButton(f"{theme_name} - {display_name}")
            radio.setProperty('theme_name', theme_name)
            radio.setProperty('is_dark', True)
            self.dark_buttons.addButton(radio)
            dark_layout.addWidget(radio)
        
        content_layout.addWidget(dark_group)
        content_layout.addStretch()
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        # 连接信号
        self.light_buttons.buttonClicked.connect(self._on_theme_selected)
        self.dark_buttons.buttonClicked.connect(self._on_theme_selected)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        apply_btn = QPushButton("应用")
        apply_btn.setDefault(True)
        apply_btn.clicked.connect(self.accept)
        btn_layout.addWidget(apply_btn)
        
        layout.addLayout(btn_layout)
    
    def _load_current_theme(self):
        """加载当前主题"""
        # 尝试从设置加载
        from PyQt6.QtCore import QSettings
        settings = QSettings("BBCode", "IDE")
        current_theme = settings.value("theme/name", "Modern Dark")
        
        # 查找并选中当前主题
        for button in self.light_buttons.buttons():
            if button.property('theme_name') == current_theme:
                button.setChecked(True)
                self._selected_theme = current_theme
                self._is_dark = False
                return
        
        for button in self.dark_buttons.buttons():
            if button.property('theme_name') == current_theme:
                button.setChecked(True)
                self._selected_theme = current_theme
                self._is_dark = True
                return
        
        # 默认选中第一个深色主题
        for button in self.dark_buttons.buttons():
            if button.property('theme_name') == "Modern Dark":
                button.setChecked(True)
                self._selected_theme = "Modern Dark"
                self._is_dark = True
                break
    
    def _on_theme_selected(self, button):
        """主题被选中"""
        self._selected_theme = button.property('theme_name')
        self._is_dark = button.property('is_dark')
    
    def get_selected_theme(self) -> str:
        """获取选中的主题名称"""
        return self._selected_theme
    
    def is_dark_theme(self) -> bool:
        """是否是深色主题"""
        return self._is_dark
