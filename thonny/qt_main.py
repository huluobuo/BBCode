# -*- coding: utf-8 -*-
"""
BBCode PyQt6 主入口
整合所有 PyQt6 组件的完整 IDE
与原版功能保持一致
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from PyQt6.QtWidgets import QApplication, QDockWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# 导入主题系统
from thonny.qt_themes import apply_theme, get_theme_manager

# 导入核心组件
from thonny.qt_workbench import QtWorkbench, FileExplorer
from thonny.qt_core import set_workbench, set_shell, set_runner, get_version
from thonny.qt_runner import Runner, get_runner

# 导入启动动画
from thonny.splash_screen import get_loading_manager

# 导入插件组件
from plugins.qt_chat import AIChatWidget
from plugins.qt_terminal import TerminalWidget, TerminalMode


class BBCodeQtApp:
    """BBCode PyQt6 应用程序 - 与原版功能一致"""
    
    def __init__(self):
        # 创建应用
        self.app = QApplication(sys.argv)
        
        # 设置应用信息
        self.app.setApplicationName("BBCode")
        self.app.setApplicationVersion(get_version())
        self.app.setOrganizationName("BBCode")
        
        # 显示启动动画
        self.loading = get_loading_manager()
        self.loading.show_splash()
        
        # 应用主题
        self.loading.update("正在初始化主题...")
        apply_theme(self.app, "dark")
        
        # 创建 Runner（必须在 Workbench 之前）
        self.loading.update("正在加载运行环境...")
        self.runner = Runner()
        set_runner(self.runner)
        
        # 创建主窗口
        self.loading.update("正在准备界面...")
        self.workbench = QtWorkbench()
        set_workbench(self.workbench)
        
        # 设置中央部件（编辑器）
        self.workbench._setup_ui()
        
        # 集成停靠窗口组件
        self._setup_dock_widgets()
        
        # 加载设置
        self.workbench._load_settings()
        
        # 创建初始编辑器
        self.workbench._editor_tabs.create_new_tab()
        
        # 连接 Runner 信号
        self._setup_runner_connections()
        
        # 完成加载
        self.loading.finish()
    
    def _setup_dock_widgets(self):
        """设置所有停靠窗口 - 支持自定义布局"""
        # === 左侧：文件浏览器 ===
        self.file_explorer = FileExplorer()
        file_dock = QDockWidget("📁 文件浏览器", self.workbench)
        file_dock.setWidget(self.file_explorer)
        file_dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea |
            Qt.DockWidgetArea.RightDockWidgetArea
        )
        self.workbench.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, file_dock)
        self.workbench.set_file_explorer(self.file_explorer, file_dock)

        # === 右侧：AI 编程助手 ===
        self.ai_chat = AIChatWidget()
        ai_dock = QDockWidget("🤖 AI 编程助手", self.workbench)
        ai_dock.setWidget(self.ai_chat)
        ai_dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea |
            Qt.DockWidgetArea.RightDockWidgetArea
        )
        self.workbench.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, ai_dock)
        self.workbench.set_ai_chat(self.ai_chat, ai_dock)

        # 连接信号
        self.ai_chat.message_sent.connect(self._on_ai_message)
        self.ai_chat.quick_action_triggered.connect(self._on_quick_action)

        # === 底部：终端 ===
        self.terminal = TerminalWidget()
        terminal_dock = QDockWidget("⌨ Shell", self.workbench)
        terminal_dock.setWidget(self.terminal)
        terminal_dock.setAllowedAreas(
            Qt.DockWidgetArea.TopDockWidgetArea |
            Qt.DockWidgetArea.BottomDockWidgetArea
        )
        self.workbench.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, terminal_dock)
        self.workbench.set_terminal(self.terminal, terminal_dock)

        # 设置全局 shell
        set_shell(self.terminal)

        # 调整分割器大小
        self.workbench._central_splitter.setSizes([250, 900, 350])

        # 允许用户自由拖拽和重新排列停靠窗口
        self.workbench.setDockNestingEnabled(True)
    
    def _setup_runner_connections(self):
        """设置 Runner 连接"""
        # 连接运行按钮
        self.workbench._run_action = lambda: self.runner.run_current_script()
        self.workbench._debug_action = lambda: self.runner.debug_current_script()
        
        # 连接停止按钮
        self.workbench._stop_action = lambda: self.runner.stop_execution()
    
    def _on_ai_message(self, message: str):
        """AI 消息处理 - 由 Ollama 处理"""
        # Ollama 会自动处理消息，这里不需要额外操作
        pass
    
    def _on_quick_action(self, action_id: str):
        """快捷操作处理"""
        # 获取当前编辑器中的代码
        editor = self.workbench._editor_tabs.get_current_editor()
        if editor:
            code = editor.get_text()
            # 将代码发送到 AI 进行分析
            self.ai_chat._send_to_ollama(
                f"请{action_id}这段代码",
                code[:2000]  # 限制代码长度
            )
    
    def run(self):
        """运行应用"""
        self.workbench.show()
        return self.app.exec()


def main():
    """主函数"""
    app = BBCodeQtApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
