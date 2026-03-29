# -*- coding: utf-8 -*-
"""
云知识库插件
将云知识库功能集成到主界面
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QMenu, QMessageBox, QApplication, QToolButton
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QAction

from thonny import get_workbench
from thonny.workbench import Workbench

from plugins.cloud_kb_settings import show_cloud_kb_settings
from plugins.cloud_kb_client import get_cloud_kb_client
from plugins.knowledge_base import get_knowledge_base


class AutoSyncWorker(QThread):
    """自动同步工作线程"""
    
    sync_finished = pyqtSignal(bool, str)
    
    def __init__(self):
        super().__init__()
        self._kb = get_knowledge_base()
    
    def run(self):
        """执行同步"""
        success, message = self._kb.sync_from_cloud()
        self.sync_finished.emit(success, message)


class CloudKBToolbarWidget(QWidget):
    """云知识库工具栏组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._client = get_cloud_kb_client()
        self._kb = get_knowledge_base()
        self._sync_worker: Optional[AutoSyncWorker] = None
        
        self._setup_ui()
        self._update_status()
    
    def _setup_ui(self):
        """设置UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(8)
        
        # 云图标按钮
        self._cloud_btn = QToolButton()
        self._cloud_btn.setText("☁️")
        self._cloud_btn.setToolTip("云知识库")
        self._cloud_btn.setStyleSheet("""
            QToolButton {
                font-size: 16px;
                padding: 4px 8px;
                border: 1px solid #555;
                border-radius: 4px;
                background-color: #3c3c3c;
            }
            QToolButton:hover {
                background-color: #4c4c4c;
            }
        """)
        self._cloud_btn.clicked.connect(self._show_cloud_menu)
        layout.addWidget(self._cloud_btn)
        
        # 状态标签
        self._status_label = QLabel("未配置")
        self._status_label.setStyleSheet("color: #858585; font-size: 12px;")
        layout.addWidget(self._status_label)
        
        # 同步按钮
        self._sync_btn = QPushButton("同步")
        self._sync_btn.setFixedWidth(50)
        self._sync_btn.setStyleSheet("""
            QPushButton {
                background-color: #4ec9b0;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #5dd9c0;
            }
            QPushButton:disabled {
                background-color: #555;
                color: #888;
            }
        """)
        self._sync_btn.clicked.connect(self._start_sync)
        layout.addWidget(self._sync_btn)
        
        layout.addStretch()
    
    def _show_cloud_menu(self):
        """显示云知识库菜单"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #3c3c3c;
                color: #d4d4d4;
                border: 1px solid #555;
            }
            QMenu::item {
                padding: 6px 20px;
            }
            QMenu::item:selected {
                background-color: #007acc;
            }
            QMenu::separator {
                height: 1px;
                background-color: #555;
                margin: 4px 0;
            }
        """)
        
        # 设置
        settings_action = QAction("⚙️ 云知识库设置...", self)
        settings_action.triggered.connect(self._open_settings)
        menu.addAction(settings_action)
        
        # 同步
        sync_action = QAction("🔄 立即同步", self)
        sync_action.triggered.connect(self._start_sync)
        menu.addAction(sync_action)
        
        menu.addSeparator()
        
        # 状态信息
        if self._kb.is_cloud_sync_enabled():
            status_action = QAction("✅ 云端同步已启用", self)
            status_action.setEnabled(False)
        else:
            status_action = QAction("⚠️ 云端同步未启用", self)
            status_action.setEnabled(False)
        menu.addAction(status_action)
        
        # 上次同步时间
        last_sync = self._kb.get_last_sync_time()
        if last_sync:
            sync_time_action = QAction(f"🕐 上次同步: {last_sync[:19].replace('T', ' ')}", self)
            sync_time_action.setEnabled(False)
            menu.addAction(sync_time_action)
        
        menu.exec(self._cloud_btn.mapToGlobal(self._cloud_btn.rect().bottomLeft()))
    
    def _open_settings(self):
        """打开设置对话框"""
        show_cloud_kb_settings(self)
        self._update_status()
    
    def _start_sync(self):
        """开始同步"""
        if not self._kb.is_cloud_sync_enabled():
            reply = QMessageBox.question(
                self,
                "云知识库未启用",
                "云端同步未启用或未配置。是否打开设置？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self._open_settings()
            return
        
        self._sync_btn.setEnabled(False)
        self._sync_btn.setText("同步中...")
        self._status_label.setText("正在同步...")
        self._status_label.setStyleSheet("color: #dcdcaa; font-size: 12px;")
        
        # 启动同步线程
        self._sync_worker = AutoSyncWorker()
        self._sync_worker.sync_finished.connect(self._on_sync_finished)
        self._sync_worker.start()
    
    def _on_sync_finished(self, success: bool, message: str):
        """同步完成回调"""
        self._sync_btn.setEnabled(True)
        self._sync_btn.setText("同步")
        self._update_status()
        
        if success:
            QMessageBox.information(self, "同步成功", message)
        else:
            QMessageBox.warning(self, "同步失败", message)
    
    def _update_status(self):
        """更新状态显示"""
        if self._kb.is_cloud_sync_enabled():
            self._status_label.setText("已连接")
            self._status_label.setStyleSheet("color: #4ec9b0; font-size: 12px;")
            self._sync_btn.setEnabled(True)
        elif self._client.is_configured():
            self._status_label.setText("已配置")
            self._status_label.setStyleSheet("color: #dcdcaa; font-size: 12px;")
            self._sync_btn.setEnabled(True)
        else:
            self._status_label.setText("未配置")
            self._status_label.setStyleSheet("color: #858585; font-size: 12px;")
            self._sync_btn.setEnabled(False)


class CloudKBPlugin:
    """云知识库插件"""
    
    def __init__(self):
        self._toolbar_widget: Optional[CloudKBToolbarWidget] = None
    
    def load(self):
        """加载插件"""
        workbench = get_workbench()
        
        # 添加工具栏组件
        self._add_toolbar_widget(workbench)
        
        # 添加菜单项
        self._add_menu_items(workbench)
        
        # 尝试自动同步
        self._try_auto_sync()
    
    def _add_toolbar_widget(self, workbench: Workbench):
        """添加工具栏组件"""
        try:
            # 尝试添加到主窗口的工具栏区域
            self._toolbar_widget = CloudKBToolbarWidget()
            
            # 查找主窗口的布局
            main_window = workbench.get_main_window()
            if main_window:
                # 尝试找到合适的位置插入
                central = main_window.centralWidget()
                if central:
                    layout = central.layout()
                    if layout:
                        # 在布局顶部插入
                        layout.insertWidget(0, self._toolbar_widget)
        except Exception as e:
            print(f"添加工具栏组件失败: {e}")
    
    def _add_menu_items(self, workbench: Workbench):
        """添加菜单项"""
        try:
            # 在工具菜单中添加
            tools_menu = workbench.get_menu("tools")
            if tools_menu:
                tools_menu.addSeparator()
                
                cloud_kb_action = QAction("云知识库设置...", tools_menu)
                cloud_kb_action.triggered.connect(lambda: show_cloud_kb_settings())
                tools_menu.addAction(cloud_kb_action)
                
                sync_action = QAction("同步云知识库", tools_menu)
                sync_action.triggered.connect(self._manual_sync)
                tools_menu.addAction(sync_action)
        except Exception as e:
            print(f"添加菜单项失败: {e}")
    
    def _manual_sync(self):
        """手动同步"""
        kb = get_knowledge_base()
        if not kb.is_cloud_sync_enabled():
            reply = QMessageBox.question(
                None,
                "云知识库未启用",
                "云端同步未启用或未配置。是否打开设置？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                show_cloud_kb_settings()
            return
        
        # 显示进度对话框
        from PyQt6.QtWidgets import QProgressDialog
        progress = QProgressDialog("正在同步云知识库...", "取消", 0, 0)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setWindowTitle("同步中")
        progress.show()
        
        # 在后台线程中同步
        def do_sync():
            success, message = kb.sync_from_cloud()
            return success, message
        
        from concurrent.futures import ThreadPoolExecutor
        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(do_sync)
        
        def check_result():
            if future.done():
                progress.close()
                success, message = future.result()
                if success:
                    QMessageBox.information(None, "同步成功", message)
                else:
                    QMessageBox.warning(None, "同步失败", message)
                executor.shutdown()
            else:
                from PyQt6.QtCore import QTimer
                QTimer.singleShot(100, check_result)
        
        check_result()
    
    def _try_auto_sync(self):
        """尝试自动同步"""
        try:
            kb = get_knowledge_base()
            if kb.is_cloud_sync_enabled():
                # 在后台静默同步
                def auto_sync():
                    success, message = kb.sync_from_cloud()
                    if success:
                        print(f"自动同步成功: {message}")
                    else:
                        print(f"自动同步失败: {message}")
                
                from concurrent.futures import ThreadPoolExecutor
                executor = ThreadPoolExecutor(max_workers=1)
                executor.submit(auto_sync)
                executor.shutdown(wait=False)
        except Exception as e:
            print(f"自动同步失败: {e}")


# 插件实例
_plugin_instance: Optional[CloudKBPlugin] = None


def load_plugin():
    """加载插件"""
    global _plugin_instance
    _plugin_instance = CloudKBPlugin()
    _plugin_instance.load()


# 兼容性导入
try:
    from typing import Optional
except ImportError:
    pass
