# -*- coding: utf-8 -*-
"""
BBCode 设置对话框
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTabWidget, QWidget, QFormLayout, QSpinBox,
    QCheckBox, QComboBox, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, QSettings


class SettingsDialog(QDialog):
    """设置对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("设置")
        self.setFixedSize(500, 400)
        
        self._settings = QSettings("BBCode", "IDE")
        
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # 标签页
        self._tabs = QTabWidget()
        layout.addWidget(self._tabs)
        
        # 通用设置
        self._general_tab = self._create_general_tab()
        self._tabs.addTab(self._general_tab, "通用")
        
        # AI设置
        self._ai_tab = self._create_ai_tab()
        self._tabs.addTab(self._ai_tab, "AI 助手")
        
        # 编辑器设置
        self._editor_tab = self._create_editor_tab()
        self._tabs.addTab(self._editor_tab, "编辑器")
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self._ok_btn = QPushButton("确定")
        self._ok_btn.clicked.connect(self._save_settings)
        btn_layout.addWidget(self._ok_btn)
        
        self._cancel_btn = QPushButton("取消")
        self._cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self._cancel_btn)
        
        layout.addLayout(btn_layout)
    
    def _create_general_tab(self) -> QWidget:
        """创建通用设置标签页"""
        tab = QWidget()
        main_layout = QVBoxLayout(tab)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        layout = QFormLayout()
        layout.setSpacing(10)
        
        # 默认文件夹
        self._default_folder = QLineEdit()
        self._default_folder.setPlaceholderText("启动时打开的文件夹")
        
        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(self._browse_folder)
        
        folder_layout = QHBoxLayout()
        folder_layout.addWidget(self._default_folder)
        folder_layout.addWidget(browse_btn)
        layout.addRow("默认文件夹:", folder_layout)
        
        # 自动保存
        self._auto_save = QCheckBox("启用自动保存")
        layout.addRow(self._auto_save)
        
        # 自动保存间隔
        self._auto_save_interval = QSpinBox()
        self._auto_save_interval.setRange(1, 60)
        self._auto_save_interval.setSuffix(" 分钟")
        layout.addRow("自动保存间隔:", self._auto_save_interval)
        
        # 显示启动动画
        self._show_splash = QCheckBox("显示启动动画")
        layout.addRow(self._show_splash)
        
        main_layout.addLayout(layout)
        main_layout.addStretch()
        return tab
    
    def _create_ai_tab(self) -> QWidget:
        """创建AI设置标签页"""
        tab = QWidget()
        main_layout = QVBoxLayout(tab)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        layout = QFormLayout()
        layout.setSpacing(10)
        
        # Ollama URL
        self._ollama_url = QLineEdit()
        self._ollama_url.setPlaceholderText("http://localhost:11434")
        layout.addRow("Ollama 地址:", self._ollama_url)
        
        # 默认模型
        self._default_model = QLineEdit()
        self._default_model.setPlaceholderText("qwen2.5-coder:7b")
        layout.addRow("默认模型:", self._default_model)
        
        # 回复语言
        self._reply_language = QComboBox()
        self._reply_language.addItems(["中文", "英文", "自动检测"])
        layout.addRow("回复语言:", self._reply_language)
        
        main_layout.addLayout(layout)
        main_layout.addStretch()
        return tab
    
    def _create_editor_tab(self) -> QWidget:
        """创建编辑器设置标签页"""
        tab = QWidget()
        main_layout = QVBoxLayout(tab)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        layout = QFormLayout()
        layout.setSpacing(10)
        
        # 字体大小
        self._font_size = QSpinBox()
        self._font_size.setRange(8, 32)
        self._font_size.setSuffix(" px")
        layout.addRow("字体大小:", self._font_size)
        
        # Tab宽度
        self._tab_width = QSpinBox()
        self._tab_width.setRange(2, 8)
        self._tab_width.setSuffix(" 空格")
        layout.addRow("Tab 宽度:", self._tab_width)
        
        # 显示行号
        self._show_line_numbers = QCheckBox("显示行号")
        layout.addRow(self._show_line_numbers)
        
        # 自动换行
        self._word_wrap = QCheckBox("自动换行")
        layout.addRow(self._word_wrap)
        
        # 语法检查
        self._syntax_check = QCheckBox("启用实时语法检查")
        layout.addRow(self._syntax_check)
        
        main_layout.addLayout(layout)
        main_layout.addStretch()
        return tab
    
    def _browse_folder(self):
        """浏览文件夹"""
        folder = QFileDialog.getExistingDirectory(self, "选择默认文件夹")
        if folder:
            self._default_folder.setText(folder)
    
    def _load_settings(self):
        """加载设置"""
        # 通用设置
        self._default_folder.setText(self._settings.value("defaultFolder", ""))
        self._auto_save.setChecked(self._settings.value("autoSave", True) == "true")
        self._auto_save_interval.setValue(int(self._settings.value("autoSaveInterval", 5)))
        self._show_splash.setChecked(self._settings.value("showSplash", True) == "true")
        
        # AI设置
        self._ollama_url.setText(self._settings.value("ollamaUrl", "http://localhost:11434"))
        self._default_model.setText(self._settings.value("defaultModel", "qwen2.5-coder:7b"))
        lang = self._settings.value("replyLanguage", "中文")
        self._reply_language.setCurrentText(lang)
        
        # 编辑器设置
        self._font_size.setValue(int(self._settings.value("fontSize", 12)))
        self._tab_width.setValue(int(self._settings.value("tabWidth", 4)))
        self._show_line_numbers.setChecked(self._settings.value("showLineNumbers", True) == "true")
        self._word_wrap.setChecked(self._settings.value("wordWrap", False) == "true")
        self._syntax_check.setChecked(self._settings.value("syntaxCheck", True) == "true")
    
    def _save_settings(self):
        """保存设置"""
        # 通用设置
        self._settings.setValue("defaultFolder", self._default_folder.text())
        self._settings.setValue("autoSave", str(self._auto_save.isChecked()).lower())
        self._settings.setValue("autoSaveInterval", self._auto_save_interval.value())
        self._settings.setValue("showSplash", str(self._show_splash.isChecked()).lower())
        
        # AI设置
        self._settings.setValue("ollamaUrl", self._ollama_url.text())
        self._settings.setValue("defaultModel", self._default_model.text())
        self._settings.setValue("replyLanguage", self._reply_language.currentText())
        
        # 编辑器设置
        self._settings.setValue("fontSize", self._font_size.value())
        self._settings.setValue("tabWidth", self._tab_width.value())
        self._settings.setValue("showLineNumbers", str(self._show_line_numbers.isChecked()).lower())
        self._settings.setValue("wordWrap", str(self._word_wrap.isChecked()).lower())
        self._settings.setValue("syntaxCheck", str(self._syntax_check.isChecked()).lower())
        
        QMessageBox.information(self, "设置", "设置已保存")
        self.accept()
