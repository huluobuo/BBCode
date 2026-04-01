# -*- coding: utf-8 -*-
"""
云知识库设置对话框
配置云端服务器连接和同步选项
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QMessageBox, QGroupBox,
    QFormLayout, QProgressBar, QTextEdit, QWidget
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

from plugins.cloud_kb_client import get_cloud_kb_client, SyncResult
from plugins.knowledge_base import get_knowledge_base


class SyncWorker(QThread):
    """同步工作线程"""
    
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, kb_dir: str):
        super().__init__()
        self.kb_dir = kb_dir
        self._client = get_cloud_kb_client()
    
    def run(self):
        """执行同步"""
        self.progress.emit("正在连接云端服务器...")
        
        # 测试连接
        success, message = self._client.test_connection()
        if not success:
            self.finished.emit(False, f"连接失败: {message}")
            return
        
        self.progress.emit("连接成功，开始同步...")
        
        # 执行同步
        result = self._client.sync_from_cloud(self.kb_dir)
        
        if result.success:
            self.finished.emit(True, result.message)
        else:
            self.finished.emit(False, result.message)


class CloudKBSettingsDialog(QDialog):
    """云知识库设置对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("云知识库设置")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        self._client = get_cloud_kb_client()
        self._kb = get_knowledge_base()
        self._sync_worker: Optional[SyncWorker] = None
        
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 服务器设置组
        server_group = QGroupBox("服务器设置")
        server_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        form_layout = QFormLayout(server_group)
        form_layout.setSpacing(10)
        
        # 服务器地址
        self._server_url_input = QLineEdit()
        self._server_url_input.setPlaceholderText("https://your-server.com")
        self._server_url_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #555;
                border-radius: 4px;
                background-color: #3c3c3c;
                color: #d4d4d4;
            }
        """)
        form_layout.addRow("服务器地址:", self._server_url_input)
        
        # API密钥（可选）
        self._api_key_input = QLineEdit()
        self._api_key_input.setPlaceholderText("可选 - 如果服务器需要认证则填写")
        self._api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._api_key_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #555;
                border-radius: 4px;
                background-color: #3c3c3c;
                color: #d4d4d4;
            }
        """)
        form_layout.addRow("API密钥(可选):", self._api_key_input)
        
        # 显示/隐藏密码按钮
        show_key_btn = QPushButton("显示")
        show_key_btn.setFixedWidth(60)
        show_key_btn.setCheckable(True)
        show_key_btn.toggled.connect(self._toggle_key_visibility)
        show_key_btn.setStyleSheet("""
            QPushButton {
                background-color: #3c3c3c;
                color: #d4d4d4;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #4c4c4c;
            }
        """)
        
        key_layout = QHBoxLayout()
        key_layout.addWidget(self._api_key_input)
        key_layout.addWidget(show_key_btn)
        form_layout.addRow("", key_layout)
        
        # 认证状态标签
        self._auth_status_label = QLabel("未检测")
        self._auth_status_label.setStyleSheet("color: #858585; font-size: 12px;")
        form_layout.addRow("认证状态:", self._auth_status_label)
        
        layout.addWidget(server_group)
        
        # 同步设置组
        sync_group = QGroupBox("同步设置")
        sync_group.setStyleSheet(server_group.styleSheet())
        
        sync_layout = QVBoxLayout(sync_group)
        
        # 启用同步
        self._sync_enabled_checkbox = QCheckBox("启用云端同步")
        self._sync_enabled_checkbox.setStyleSheet("color: #d4d4d4;")
        sync_layout.addWidget(self._sync_enabled_checkbox)
        
        # 同步状态
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("同步状态:"))
        self._sync_status_label = QLabel("未配置")
        self._sync_status_label.setStyleSheet("color: #858585;")
        status_layout.addWidget(self._sync_status_label)
        status_layout.addStretch()
        sync_layout.addLayout(status_layout)
        
        # 上次同步时间
        last_sync_layout = QHBoxLayout()
        last_sync_layout.addWidget(QLabel("上次同步:"))
        self._last_sync_label = QLabel("从未")
        self._last_sync_label.setStyleSheet("color: #858585;")
        last_sync_layout.addWidget(self._last_sync_label)
        last_sync_layout.addStretch()
        sync_layout.addLayout(last_sync_layout)
        
        layout.addWidget(sync_group)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        
        self._test_btn = QPushButton("测试连接")
        self._test_btn.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #0098ff;
            }
        """)
        self._test_btn.clicked.connect(self._test_connection)
        btn_layout.addWidget(self._test_btn)
        
        self._sync_btn = QPushButton("立即同步")
        self._sync_btn.setStyleSheet("""
            QPushButton {
                background-color: #4ec9b0;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #5dd9c0;
            }
            QPushButton:disabled {
                background-color: #555;
            }
        """)
        self._sync_btn.clicked.connect(self._start_sync)
        btn_layout.addWidget(self._sync_btn)
        
        btn_layout.addStretch()
        
        self._save_btn = QPushButton("保存设置")
        self._save_btn.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #0098ff;
            }
        """)
        self._save_btn.clicked.connect(self._save_settings)
        btn_layout.addWidget(self._save_btn)
        
        self._cancel_btn = QPushButton("取消")
        self._cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #3c3c3c;
                color: #d4d4d4;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #4c4c4c;
            }
        """)
        self._cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self._cancel_btn)
        
        layout.addLayout(btn_layout)
        
        # 进度和日志区域
        self._progress_widget = QWidget()
        self._progress_widget.setVisible(False)
        progress_layout = QVBoxLayout(self._progress_widget)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        
        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 0)  # 无限进度
        self._progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #555;
                border-radius: 4px;
                text-align: center;
                color: #d4d4d4;
            }
            QProgressBar::chunk {
                background-color: #007acc;
            }
        """)
        progress_layout.addWidget(self._progress_bar)
        
        self._log_text = QTextEdit()
        self._log_text.setMaximumHeight(80)
        self._log_text.setReadOnly(True)
        self._log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 5px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
        """)
        progress_layout.addWidget(self._log_text)
        
        layout.addWidget(self._progress_widget)
        
        layout.addStretch()
        
        # 设置对话框样式
        self.setStyleSheet("""
            QDialog {
                background-color: #2d2d2d;
            }
            QLabel {
                color: #d4d4d4;
            }
        """)
    
    def _toggle_key_visibility(self, checked):
        """切换API密钥可见性"""
        if checked:
            self._api_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.sender().setText("隐藏")
        else:
            self._api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.sender().setText("显示")
    
    def _load_settings(self):
        """加载设置"""
        try:
            from PyQt6.QtCore import QSettings
            settings = QSettings("BBCode", "IDE")
            
            server_url = settings.value("cloud_kb.server_url", "")
            api_key = settings.value("cloud_kb.api_key", "")
            sync_enabled = settings.value("cloud_kb.sync_enabled", False) in [True, "true", "True"]
            
            self._server_url_input.setText(server_url)
            self._api_key_input.setText(api_key)
            self._sync_enabled_checkbox.setChecked(sync_enabled)
            
            # 更新状态显示
            self._update_status_display()
            
        except Exception as e:
            print(f"加载设置失败: {e}")
    
    def _update_status_display(self):
        """更新状态显示"""
        if self._client.is_configured():
            if self._sync_enabled_checkbox.isChecked():
                self._sync_status_label.setText("已启用")
                self._sync_status_label.setStyleSheet("color: #4ec9b0;")
            else:
                self._sync_status_label.setText("已配置但未启用")
                self._sync_status_label.setStyleSheet("color: #dcdcaa;")
        else:
            self._sync_status_label.setText("未配置")
            self._sync_status_label.setStyleSheet("color: #858585;")
        
        # 上次同步时间
        last_sync = self._kb.get_last_sync_time()
        if last_sync:
            self._last_sync_label.setText(last_sync[:19].replace('T', ' '))
        else:
            self._last_sync_label.setText("从未")
    
    def _test_connection(self):
        """测试连接"""
        server_url = self._server_url_input.text().strip()
        api_key = self._api_key_input.text().strip()
        
        if not server_url:
            QMessageBox.warning(self, "警告", "请输入服务器地址")
            return
        
        # API密钥现在是可选的
        # 临时设置凭证
        self._client.set_credentials(server_url, api_key)
        
        self._test_btn.setEnabled(False)
        self._test_btn.setText("测试中...")
        
        # 在后台线程中测试
        def test():
            success, message = self._client.test_connection()
            return success, message
        
        from PyQt6.QtCore import QThreadPool
        from concurrent.futures import ThreadPoolExecutor
        
        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(test)
        
        def check_result():
            if future.done():
                success, message = future.result()
                self._test_btn.setEnabled(True)
                self._test_btn.setText("测试连接")
                
                if success:
                    # 更新认证状态显示
                    if "无需认证" in message:
                        self._auth_status_label.setText("✅ 无需认证")
                        self._auth_status_label.setStyleSheet("color: #4ec9b0; font-size: 12px;")
                    else:
                        self._auth_status_label.setText("🔒 需要认证")
                        self._auth_status_label.setStyleSheet("color: #dcdcaa; font-size: 12px;")
                    
                    QMessageBox.information(self, "成功", f"连接成功!\n{message}")
                else:
                    self._auth_status_label.setText("❌ 连接失败")
                    self._auth_status_label.setStyleSheet("color: #f44336; font-size: 12px;")
                    QMessageBox.critical(self, "失败", f"连接失败:\n{message}")
                executor.shutdown()
            else:
                from PyQt6.QtCore import QTimer
                QTimer.singleShot(100, check_result)
        
        check_result()
    
    def _start_sync(self):
        """开始同步"""
        if not self._client.is_configured():
            QMessageBox.warning(self, "警告", "请先配置服务器地址和API密钥")
            return
        
        self._sync_btn.setEnabled(False)
        self._test_btn.setEnabled(False)
        self._progress_widget.setVisible(True)
        self._log_text.clear()
        self._log("开始同步...")
        
        # 创建工作线程
        self._sync_worker = SyncWorker(self._kb.kb_dir)
        self._sync_worker.progress.connect(self._log)
        self._sync_worker.finished.connect(self._on_sync_finished)
        self._sync_worker.start()
    
    def _log(self, message: str):
        """添加日志"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self._log_text.append(f"[{timestamp}] {message}")
    
    def _on_sync_finished(self, success: bool, message: str):
        """同步完成回调"""
        self._sync_btn.setEnabled(True)
        self._test_btn.setEnabled(True)
        self._progress_bar.setVisible(False)
        
        self._log(message)
        
        if success:
            QMessageBox.information(self, "同步完成", message)
            self._update_status_display()
        else:
            QMessageBox.critical(self, "同步失败", message)
    
    def _save_settings(self):
        """保存设置"""
        server_url = self._server_url_input.text().strip()
        api_key = self._api_key_input.text().strip()
        sync_enabled = self._sync_enabled_checkbox.isChecked()
        
        try:
            from PyQt6.QtCore import QSettings
            settings = QSettings("BBCode", "IDE")
            
            settings.setValue("cloud_kb.server_url", server_url)
            settings.setValue("cloud_kb.api_key", api_key)
            settings.setValue("cloud_kb.sync_enabled", sync_enabled)
            
            # 更新客户端凭证
            self._client.set_credentials(server_url, api_key)
            
            # 更新知识库设置
            self._kb.update_cloud_credentials(server_url, api_key)
            self._kb.set_cloud_sync_enabled(sync_enabled)
            
            QMessageBox.information(self, "成功", "设置已保存")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存设置失败:\n{str(e)}")


def show_cloud_kb_settings(parent=None):
    """显示云知识库设置对话框"""
    dialog = CloudKBSettingsDialog(parent)
    return dialog.exec()


# 兼容性导入
try:
    from typing import Optional
except ImportError:
    pass
