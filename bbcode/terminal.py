# -*- coding: utf-8 -*-
"""
BBCode 终端组件
使用 QProcess 运行真实的 Python 解释器
"""

import sys
import os
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QComboBox, QLabel, QLineEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QProcess
from PyQt6.QtGui import QTextCursor, QFont, QColor


class Terminal(QWidget):
    """终端组件 - 使用 QProcess 运行真实 Python"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._process: QProcess = None
        self._current_mode = "python"
        self._history: list = []
        self._history_index = 0
        
        self._setup_ui()
        self._start_process()
    
    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # 工具栏
        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(8, 4, 8, 4)
        
        toolbar.addWidget(QLabel("模式:"))
        
        self._mode_combo = QComboBox()
        self._mode_combo.addItems(["Python", "系统命令"])
        self._mode_combo.currentTextChanged.connect(self._on_mode_changed)
        toolbar.addWidget(self._mode_combo)
        
        toolbar.addStretch()
        
        restart_btn = QPushButton("重启")
        restart_btn.clicked.connect(self._restart_process)
        toolbar.addWidget(restart_btn)
        
        clear_btn = QPushButton("清空")
        clear_btn.clicked.connect(self._clear_terminal)
        toolbar.addWidget(clear_btn)
        
        layout.addLayout(toolbar)
        
        # 输出显示区域
        self._output = QTextEdit()
        self._output.setReadOnly(True)
        self._output.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        
        font = QFont("Consolas", 10)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self._output.setFont(font)
        
        self._output.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: none;
            }
        """)
        
        layout.addWidget(self._output, 1)
        
        # 输入区域
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(5, 5, 5, 5)
        
        self._prompt_label = QLabel(">>> ")
        self._prompt_label.setStyleSheet("color: #569cd6; font-family: Consolas;")
        input_layout.addWidget(self._prompt_label)
        
        self._input = QLineEdit()
        self._input.setStyleSheet("""
            QLineEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #3c3c3c;
                border-radius: 3px;
                padding: 5px;
                font-family: Consolas;
            }
        """)
        self._input.returnPressed.connect(self._on_return_pressed)
        input_layout.addWidget(self._input, 1)
        
        layout.addLayout(input_layout)
    
    def _start_process(self):
        """启动 Python 进程"""
        self._process = QProcess(self)
        self._process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        
        # 连接信号
        self._process.readyReadStandardOutput.connect(self._read_output)
        self._process.readyReadStandardError.connect(self._read_error)
        
        # 获取 Python 路径
        python_exe = sys.executable
        
        # 启动交互式 Python
        self._process.start(python_exe, ["-i", "-u"])  # -i 交互模式, -u 无缓冲
        
        if not self._process.waitForStarted(5000):
            self._append_output("无法启动 Python 进程\n", "#ff6b6b")
    
    def _restart_process(self):
        """重启 Python 进程"""
        if self._process and self._process.state() != QProcess.ProcessState.NotRunning:
            self._process.terminate()
            self._process.waitForFinished(1000)
            self._process.kill()
        
        self._clear_terminal()
        self._start_process()
    
    def _read_output(self):
        """读取标准输出"""
        data = self._process.readAllStandardOutput()
        text = bytes(data).decode('utf-8', errors='replace')
        self._append_output(text, "#d4d4d4")
    
    def _read_error(self):
        """读取标准错误"""
        data = self._process.readAllStandardError()
        text = bytes(data).decode('utf-8', errors='replace')
        self._append_output(text, "#ff6b6b")
    
    def _on_return_pressed(self):
        """回车键处理"""
        command = self._input.text()
        self._input.clear()
        
        # 显示命令
        self._append_output(f">>> {command}\n", "#569cd6")
        
        if command.strip():
            self._history.append(command)
            self._history_index = len(self._history)
            
            if self._current_mode == "python":
                # 发送命令到 Python 进程
                if self._process and self._process.state() == QProcess.ProcessState.Running:
                    self._process.write((command + "\n").encode('utf-8'))
            else:
                self._run_system_command(command)
    
    def _run_system_command(self, command: str):
        """运行系统命令"""
        import subprocess
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=30
            )
            if result.stdout:
                self._append_output(result.stdout, "#d4d4d4")
            if result.stderr:
                self._append_output(result.stderr, "#ff6b6b")
        except Exception as e:
            self._append_output(f"Error: {e}\n", "#ff6b6b")
    
    def _append_output(self, text: str, color: str = "#d4d4d4"):
        """追加输出文本"""
        self._output.moveCursor(QTextCursor.MoveOperation.End)
        self._output.setTextColor(QColor(color))
        self._output.insertPlainText(text)
        self._output.moveCursor(QTextCursor.MoveOperation.End)
    
    def _on_mode_changed(self, mode: str):
        """模式切换"""
        self._current_mode = "python" if mode == "Python" else "system"
        self._append_output(f"\n[切换到 {mode} 模式]\n", "#4ec9b0")
    
    def _clear_terminal(self):
        """清空终端"""
        self._output.clear()
        self._append_output("BBCode Python Shell\n", "#4ec9b0")
        self._append_output(f"Python {sys.version}\n\n", "#d4d4d4")
    
    def keyPressEvent(self, event):
        """处理键盘事件 - 历史导航"""
        if self._input.hasFocus():
            key = event.key()
            if key == Qt.Key.Key_Up:
                self._navigate_history(-1)
                event.accept()
                return
            elif key == Qt.Key.Key_Down:
                self._navigate_history(1)
                event.accept()
                return
        super().keyPressEvent(event)
    
    def _navigate_history(self, direction: int):
        """导航历史记录"""
        if not self._history:
            return
        
        self._history_index += direction
        self._history_index = max(0, min(self._history_index, len(self._history)))
        
        if self._history_index < len(self._history):
            self._input.setText(self._history[self._history_index])
        else:
            self._input.clear()
    
    def closeEvent(self, event):
        """关闭事件"""
        if self._process and self._process.state() != QProcess.ProcessState.NotRunning:
            self._process.terminate()
            self._process.waitForFinished(1000)
            self._process.kill()
        event.accept()
