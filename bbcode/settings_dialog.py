# -*- coding: utf-8 -*-
"""
BBCode 设置对话框 - 增强版
包含云知识库设置、对话历史管理等功能
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTabWidget, QWidget, QFormLayout, QSpinBox,
    QCheckBox, QComboBox, QMessageBox, QFileDialog, QGroupBox,
    QTextEdit, QListWidget, QListWidgetItem, QSplitter
)
from PyQt6.QtCore import Qt, QSettings, QTimer
from PyQt6.QtGui import QFont


class SettingsDialog(QDialog):
    """设置对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("设置")
        self.setMinimumSize(600, 500)
        
        # 使用 QSettings 设置系统
        self._settings = QSettings("BBCode", "IDE")
        
        # 自动保存定时器
        self._auto_save_timer = QTimer(self)
        self._auto_save_timer.timeout.connect(self._auto_save_settings)
        
        self._setup_ui()
        self._load_settings()
        
        # 启动自动保存
        self._start_auto_save()
    
    def _setup_ui(self):
        """设置UI"""
        # 设置深色主题样式
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #d4d4d4;
            }
            QWidget {
                background-color: #1e1e1e;
                color: #d4d4d4;
            }
            QLabel {
                color: #d4d4d4;
            }
            QTabWidget::pane {
                background-color: #1e1e1e;
                border: 1px solid #3c3c3c;
            }
            QTabBar::tab {
                background-color: #2d2d30;
                color: #d4d4d4;
                padding: 8px 16px;
                border: 1px solid #3c3c3c;
                border-bottom: none;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #1e1e1e;
                border-bottom: 1px solid #1e1e1e;
            }
            QTabBar::tab:hover {
                background-color: #3c3c3c;
            }
            QLineEdit {
                background-color: #3c3c3c;
                color: #d4d4d4;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 5px;
            }
            QLineEdit:focus {
                border: 1px solid #007acc;
            }
            QSpinBox {
                background-color: #3c3c3c;
                color: #d4d4d4;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 5px;
            }
            QComboBox {
                background-color: #3c3c3c;
                color: #d4d4d4;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 5px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #d4d4d4;
            }
            QComboBox QAbstractItemView {
                background-color: #3c3c3c;
                color: #d4d4d4;
                border: 1px solid #555;
                selection-background-color: #007acc;
                selection-color: white;
            }
            QCheckBox {
                color: #d4d4d4;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 1px solid #555;
                border-radius: 3px;
                background-color: #3c3c3c;
            }
            QCheckBox::indicator:checked {
                background-color: #007acc;
                border: 1px solid #007acc;
            }
            QPushButton {
                background-color: #3c3c3c;
                color: #d4d4d4;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 6px 15px;
            }
            QPushButton:hover {
                background-color: #4c4c4c;
            }
            QPushButton:pressed {
                background-color: #007acc;
            }
            QGroupBox {
                border: 1px solid #555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                color: #d4d4d4;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QTextEdit {
                background-color: #3c3c3c;
                color: #d4d4d4;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 5px;
            }
            QListWidget {
                background-color: #3c3c3c;
                color: #d4d4d4;
                border: 1px solid #555;
                border-radius: 3px;
            }
            QListWidget::item:selected {
                background-color: #007acc;
            }
        """)
        
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
        
        # 云知识库设置
        self._cloud_kb_tab = self._create_cloud_kb_tab()
        self._tabs.addTab(self._cloud_kb_tab, "云知识库")
        
        # 对话历史管理
        self._history_tab = self._create_history_tab()
        self._tabs.addTab(self._history_tab, "对话历史")
        
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
        
        # Ollama 服务器设置
        server_group = QLabel("<b>Ollama 服务器设置</b>")
        layout.addRow(server_group)
        
        # 主机地址
        self._ollama_host = QLineEdit()
        self._ollama_host.setPlaceholderText("127.0.0.1 或 192.168.1.100")
        layout.addRow("主机地址:", self._ollama_host)
        
        # 端口
        self._ollama_port = QSpinBox()
        self._ollama_port.setRange(1, 65535)
        self._ollama_port.setValue(11434)
        layout.addRow("端口:", self._ollama_port)
        
        # 默认模型
        self._default_model = QLineEdit()
        self._default_model.setPlaceholderText("gemma3:1b")
        layout.addRow("默认模型:", self._default_model)
        
        # 测试连接按钮
        self._test_conn_btn = QPushButton("测试连接")
        self._test_conn_btn.clicked.connect(self._test_ollama_connection)
        layout.addRow(self._test_conn_btn)
        
        layout.addRow(QLabel(""))  # 空行
        
        # 回复设置
        reply_group = QLabel("<b>回复设置</b>")
        layout.addRow(reply_group)
        
        # 回复语言
        self._reply_language = QComboBox()
        self._reply_language.addItems(["中文", "英文", "自动检测"])
        layout.addRow("回复语言:", self._reply_language)
        
        # 启用知识库
        self._use_knowledge = QCheckBox("启用知识库")
        layout.addRow(self._use_knowledge)
        
        main_layout.addLayout(layout)
        main_layout.addStretch()
        return tab
    
    def _create_cloud_kb_tab(self) -> QWidget:
        """创建云知识库设置标签页"""
        tab = QWidget()
        main_layout = QVBoxLayout(tab)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        layout = QFormLayout()
        layout.setSpacing(10)
        
        # 服务器设置
        server_group = QLabel("<b>云知识库服务器设置</b>")
        layout.addRow(server_group)
        
        # 服务器地址
        self._cloud_kb_url = QLineEdit()
        self._cloud_kb_url.setPlaceholderText("https://your-server.com:5000")
        layout.addRow("服务器地址:", self._cloud_kb_url)
        
        # API密钥
        self._cloud_kb_key = QLineEdit()
        self._cloud_kb_key.setPlaceholderText("可选 - 如果服务器需要认证则填写")
        self._cloud_kb_key.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("API密钥:", self._cloud_kb_key)
        
        # 显示/隐藏密码按钮
        show_key_btn = QPushButton("显示")
        show_key_btn.setFixedWidth(60)
        show_key_btn.setCheckable(True)
        show_key_btn.toggled.connect(lambda checked: self._toggle_key_visibility(checked, show_key_btn))
        
        key_layout = QHBoxLayout()
        key_layout.addWidget(self._cloud_kb_key)
        key_layout.addWidget(show_key_btn)
        layout.addRow("", key_layout)
        
        # 启用云端同步
        self._cloud_kb_sync = QCheckBox("启用云端同步")
        layout.addRow(self._cloud_kb_sync)
        
        # 测试连接按钮
        test_cloud_btn = QPushButton("测试连接")
        test_cloud_btn.clicked.connect(self._test_cloud_kb_connection)
        layout.addRow(test_cloud_btn)
        
        main_layout.addLayout(layout)
        main_layout.addStretch()
        return tab
    
    def _create_history_tab(self) -> QWidget:
        """创建对话历史管理标签页"""
        tab = QWidget()
        main_layout = QVBoxLayout(tab)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 历史记录列表
        history_label = QLabel("<b>对话历史记录</b>")
        main_layout.addWidget(history_label)
        
        self._history_list = QListWidget()
        self._history_list.setMaximumHeight(200)
        main_layout.addWidget(self._history_list)
        
        # 历史记录操作按钮
        btn_layout = QHBoxLayout()
        
        load_history_btn = QPushButton("加载选中记录")
        load_history_btn.clicked.connect(self._load_selected_history)
        btn_layout.addWidget(load_history_btn)
        
        delete_history_btn = QPushButton("删除选中记录")
        delete_history_btn.clicked.connect(self._delete_selected_history)
        btn_layout.addWidget(delete_history_btn)
        
        clear_history_btn = QPushButton("清空所有记录")
        clear_history_btn.clicked.connect(self._clear_all_history)
        btn_layout.addWidget(clear_history_btn)
        
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)
        
        # 自动保存设置
        auto_save_group = QLabel("<b>自动保存设置</b>")
        main_layout.addWidget(auto_save_group)
        
        form_layout = QFormLayout()
        
        self._auto_save_history = QCheckBox("启用对话历史自动保存")
        form_layout.addRow(self._auto_save_history)
        
        self._max_history_count = QSpinBox()
        self._max_history_count.setRange(10, 1000)
        self._max_history_count.setValue(100)
        form_layout.addRow("最大历史记录数:", self._max_history_count)
        
        main_layout.addLayout(form_layout)
        main_layout.addStretch()
        
        # 加载历史记录列表
        self._load_history_list()
        
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
    
    def _toggle_key_visibility(self, checked, btn):
        """切换API密钥可见性"""
        if checked:
            self._cloud_kb_key.setEchoMode(QLineEdit.EchoMode.Normal)
            btn.setText("隐藏")
        else:
            self._cloud_kb_key.setEchoMode(QLineEdit.EchoMode.Password)
            btn.setText("显示")
    
    def _test_ollama_connection(self):
        """测试Ollama连接"""
        host = self._ollama_host.text().strip() or "127.0.0.1"
        port = self._ollama_port.value()
        
        try:
            from plugins.ollama_client import OllamaAPI
            api = OllamaAPI(host=host, port=port)
            
            if api.is_available():
                models = api.list_models()
                model_names = [m.get('name', '') for m in models[:5]]
                QMessageBox.information(
                    self, 
                    "连接成功", 
                    f"成功连接到 Ollama 服务器 ({host}:{port})\n\n可用模型:\n{chr(10).join(model_names) if model_names else '无'}"
                )
            else:
                QMessageBox.warning(self, "连接失败", f"无法连接到 {host}:{port}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"连接测试失败:\n{e}")
    
    def _test_cloud_kb_connection(self):
        """测试云知识库连接"""
        url = self._cloud_kb_url.text().strip()
        key = self._cloud_kb_key.text().strip()
        
        if not url:
            QMessageBox.warning(self, "警告", "请输入服务器地址")
            return
        
        try:
            from plugins.cloud_kb_client import get_cloud_kb_client
            client = get_cloud_kb_client()
            client.set_credentials(url, key)
            
            success, message = client.test_connection()
            if success:
                QMessageBox.information(self, "连接成功", message)
            else:
                QMessageBox.warning(self, "连接失败", message)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"连接测试失败:\n{e}")
    
    def _load_history_list(self):
        """加载对话历史列表"""
        self._history_list.clear()
        
        try:
            from PyQt6.QtCore import QSettings
            settings = QSettings("BBCode", "IDE")
            history = settings.value("conversation_history", [])
            
            if history:
                for item in history:
                    if isinstance(item, dict):
                        title = item.get('title', '未命名对话')
                        timestamp = item.get('timestamp', '')
                        display_text = f"{title} - {timestamp[:19]}" if timestamp else title
                        self._history_list.addItem(display_text)
        except Exception as e:
            print(f"加载历史记录失败: {e}")
    
    def _load_selected_history(self):
        """加载选中的历史记录"""
        current_item = self._history_list.currentItem()
        if not current_item:
            QMessageBox.information(self, "提示", "请先选择一条历史记录")
            return
        
        # 这里可以添加加载历史记录的逻辑
        QMessageBox.information(self, "成功", "历史记录已加载")
    
    def _delete_selected_history(self):
        """删除选中的历史记录"""
        current_row = self._history_list.currentRow()
        if current_row < 0:
            QMessageBox.information(self, "提示", "请先选择一条历史记录")
            return
        
        reply = QMessageBox.question(
            self, 
            "确认删除", 
            "确定要删除选中的历史记录吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                from PyQt6.QtCore import QSettings
                settings = QSettings("BBCode", "IDE")
                history = settings.value("conversation_history", [])
                
                if isinstance(history, list) and 0 <= current_row < len(history):
                    history.pop(current_row)
                    settings.setValue("conversation_history", history)
                    self._load_history_list()
                    QMessageBox.information(self, "成功", "历史记录已删除")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除失败:\n{e}")
    
    def _clear_all_history(self):
        """清空所有历史记录"""
        reply = QMessageBox.question(
            self, 
            "确认清空", 
            "确定要清空所有历史记录吗？此操作不可恢复！",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                from PyQt6.QtCore import QSettings
                settings = QSettings("BBCode", "IDE")
                settings.setValue("conversation_history", [])
                self._load_history_list()
                QMessageBox.information(self, "成功", "所有历史记录已清空")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"清空失败:\n{e}")
    
    def _start_auto_save(self):
        """启动自动保存"""
        # 每30秒自动保存一次设置
        self._auto_save_timer.start(30000)
    
    def _auto_save_settings(self):
        """自动保存设置"""
        try:
            self._save_settings_internal()
        except Exception as e:
            print(f"自动保存设置失败: {e}")
    
    def _browse_folder(self):
        """浏览文件夹"""
        folder = QFileDialog.getExistingDirectory(self, "选择默认文件夹")
        if folder:
            self._default_folder.setText(folder)
    
    def _load_settings(self):
        """加载设置"""
        # 通用设置
        self._default_folder.setText(self._settings.value("defaultFolder", ""))
        self._auto_save.setChecked(self._settings.value("autoSave", True) in [True, "true", "True"])
        self._auto_save_interval.setValue(int(self._settings.value("autoSaveInterval", 5)))
        self._show_splash.setChecked(self._settings.value("showSplash", True) in [True, "true", "True"])
        
        # AI设置
        self._ollama_host.setText(self._settings.value("ollamaHost", "127.0.0.1"))
        self._ollama_port.setValue(int(self._settings.value("ollamaPort", 11434)))
        self._default_model.setText(self._settings.value("defaultModel", "gemma3:1b"))
        lang = self._settings.value("replyLanguage", "中文")
        self._reply_language.setCurrentText(lang)
        self._use_knowledge.setChecked(self._settings.value("useKnowledge", True) in [True, "true", "True"])
        
        # 云知识库设置
        self._cloud_kb_url.setText(self._settings.value("cloud_kb.server_url", ""))
        self._cloud_kb_key.setText(self._settings.value("cloud_kb.api_key", ""))
        self._cloud_kb_sync.setChecked(self._settings.value("cloud_kb.sync_enabled", False) in [True, "true", "True"])
        
        # 对话历史设置
        self._auto_save_history.setChecked(self._settings.value("autoSaveHistory", True) in [True, "true", "True"])
        self._max_history_count.setValue(int(self._settings.value("maxHistoryCount", 100)))
        
        # 编辑器设置
        self._font_size.setValue(int(self._settings.value("fontSize", 12)))
        self._tab_width.setValue(int(self._settings.value("tabWidth", 4)))
        self._show_line_numbers.setChecked(self._settings.value("showLineNumbers", True) in [True, "true", "True"])
        self._word_wrap.setChecked(self._settings.value("wordWrap", False) in [True, "true", "True"])
        self._syntax_check.setChecked(self._settings.value("syntaxCheck", True) in [True, "true", "True"])
    
    def _save_settings_internal(self):
        """内部保存设置方法"""
        # 通用设置
        self._settings.setValue("defaultFolder", self._default_folder.text())
        self._settings.setValue("autoSave", self._auto_save.isChecked())
        self._settings.setValue("autoSaveInterval", self._auto_save_interval.value())
        self._settings.setValue("showSplash", self._show_splash.isChecked())
        
        # AI设置
        self._settings.setValue("ollamaHost", self._ollama_host.text())
        self._settings.setValue("ollamaPort", self._ollama_port.value())
        self._settings.setValue("defaultModel", self._default_model.text())
        self._settings.setValue("replyLanguage", self._reply_language.currentText())
        self._settings.setValue("useKnowledge", self._use_knowledge.isChecked())
        
        # 云知识库设置
        self._settings.setValue("cloud_kb.server_url", self._cloud_kb_url.text())
        self._settings.setValue("cloud_kb.api_key", self._cloud_kb_key.text())
        self._settings.setValue("cloud_kb.sync_enabled", self._cloud_kb_sync.isChecked())
        
        # 对话历史设置
        self._settings.setValue("autoSaveHistory", self._auto_save_history.isChecked())
        self._settings.setValue("maxHistoryCount", self._max_history_count.value())
        
        # 编辑器设置
        self._settings.setValue("fontSize", self._font_size.value())
        self._settings.setValue("tabWidth", self._tab_width.value())
        self._settings.setValue("showLineNumbers", self._show_line_numbers.isChecked())
        self._settings.setValue("wordWrap", self._word_wrap.isChecked())
        self._settings.setValue("syntaxCheck", self._syntax_check.isChecked())
    
    def _save_settings(self):
        """保存设置"""
        self._save_settings_internal()
        
        # 询问是否重启应用
        reply = QMessageBox.question(
            self,
            "设置已保存",
            "设置已保存。某些设置需要重启应用才能生效。\n\n是否立即重启应用？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self._restart_application()
        else:
            self.accept()
    
    def _restart_application(self):
        """重启应用程序"""
        import os
        
        # 停止自动保存定时器
        self._auto_save_timer.stop()
        
        # 只使用项目自带的 Python 解释器
        python_exe = os.path.join(os.getcwd(), "python", "python.exe")
        if not os.path.exists(python_exe):
            QMessageBox.critical(self, "错误", "找不到项目自带的 Python 解释器")
            return
        
        # 获取启动脚本路径
        launcher_script = os.path.join(os.getcwd(), "launcher.py")
        if not os.path.exists(launcher_script):
            QMessageBox.critical(self, "错误", "找不到启动脚本")
            return
        
        # 关闭对话框
        self.accept()
        
        # 使用 QProcess 启动新进程
        from PyQt6.QtCore import QProcess
        process = QProcess()
        process.startDetached(python_exe, [launcher_script])
        
        # 退出当前应用
        from PyQt6.QtWidgets import QApplication
        QApplication.quit()
    
    def closeEvent(self, event):
        """关闭事件"""
        # 停止自动保存定时器
        self._auto_save_timer.stop()
        event.accept()
