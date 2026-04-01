# -*- coding: utf-8 -*-
"""
BBCode 嵌入式终端组件 - 使用 QProcess 实现
提供基本的终端功能，支持命令输入和输出显示
"""

import sys
import os
import re
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit,
    QLabel, QFrame, QToolButton, QLineEdit
)
from PyQt6.QtCore import Qt, QProcess
from PyQt6.QtGui import QFont, QTextCursor, QKeyEvent


class Terminal(QWidget):
    """终端组件 - 使用独立的输入框和输出显示"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._process: QProcess = None
        self._command_history = []
        self._history_index = -1
        
        self._setup_ui()
        self._start_shell_process()
    
    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 顶部工具栏
        toolbar = QFrame()
        toolbar.setFixedHeight(35)
        toolbar.setStyleSheet("""
            QFrame {
                background-color: #1f1f1f;
                border-bottom: 1px solid #333;
            }
        """)
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(10, 0, 10, 0)
        toolbar_layout.setSpacing(8)
        
        # 终端标题
        title_label = QLabel("Terminal")
        title_label.setStyleSheet("color: #cccccc; font-size: 12px; font-weight: bold;")
        toolbar_layout.addWidget(title_label)
        
        # 状态指示器
        self._status_label = QLabel("●")
        self._status_label.setStyleSheet("color: #0dbc79; font-size: 10px;")
        toolbar_layout.addWidget(self._status_label)
        
        toolbar_layout.addStretch()
        
        # 清空按钮
        clear_btn = QToolButton()
        clear_btn.setText("🗑")
        clear_btn.setToolTip("清空终端")
        clear_btn.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                border: none;
                color: #cccccc;
                font-size: 14px;
                padding: 4px 8px;
            }
            QToolButton:hover {
                background-color: #3c3c3c;
                border-radius: 3px;
            }
        """)
        clear_btn.clicked.connect(self._clear_terminal)
        toolbar_layout.addWidget(clear_btn)
        
        layout.addWidget(toolbar)
        
        # 终端输出显示区域
        self._output = QPlainTextEdit()
        self._output.setReadOnly(True)
        font = QFont("Consolas", 10)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self._output.setFont(font)
        self._output.setStyleSheet("""
            QPlainTextEdit {
                background-color: #0c0c0c;
                color: #cccccc;
                border: none;
                padding: 8px;
            }
        """)
        self._output.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        layout.addWidget(self._output, stretch=1)
        
        # 输入区域
        input_frame = QFrame()
        input_frame.setStyleSheet("""
            QFrame {
                background-color: #1f1f1f;
                border-top: 1px solid #333;
            }
        """)
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(8, 4, 8, 4)
        input_layout.setSpacing(8)
        
        # 提示符标签
        prompt_label = QLabel(">")
        prompt_label.setStyleSheet("color: #0dbc79; font-weight: bold;")
        input_layout.addWidget(prompt_label)
        
        # 命令输入框
        self._input = QLineEdit()
        self._input.setStyleSheet("""
            QLineEdit {
                background-color: #0c0c0c;
                color: #cccccc;
                border: none;
                padding: 6px;
                font-family: Consolas;
                font-size: 10pt;
            }
        """)
        self._input.returnPressed.connect(self._execute_command)
        self._input.installEventFilter(self)
        input_layout.addWidget(self._input, stretch=1)
        
        layout.addWidget(input_frame)
    
    def eventFilter(self, obj, event):
        """事件过滤器 - 处理上下箭头键"""
        if obj == self._input and event.type() == event.Type.KeyPress:
            if event.key() == Qt.Key.Key_Up:
                self._history_up()
                return True
            elif event.key() == Qt.Key.Key_Down:
                self._history_down()
                return True
        return super().eventFilter(obj, event)
    
    def _history_up(self):
        """显示上一条历史命令"""
        if self._command_history and self._history_index > 0:
            self._history_index -= 1
            self._input.setText(self._command_history[self._history_index])
    
    def _history_down(self):
        """显示下一条历史命令"""
        if self._history_index < len(self._command_history) - 1:
            self._history_index += 1
            self._input.setText(self._command_history[self._history_index])
        elif self._history_index == len(self._command_history) - 1:
            self._history_index = len(self._command_history)
            self._input.clear()
    
    def _execute_command(self):
        """执行命令"""
        command = self._input.text().strip()
        if not command:
            return
        
        # 添加到历史
        self._command_history.append(command)
        self._history_index = len(self._command_history)
        
        # 显示命令
        self._output.appendPlainText(f"> {command}")
        
        # 清空输入框
        self._input.clear()
        
        # 发送命令到进程
        if self._process and self._process.state() == QProcess.ProcessState.Running:
            self._process.write((command + "\n").encode('utf-8'))
    
    def _start_shell_process(self):
        """启动 Shell 进程"""
        self._process = QProcess(self)
        self._process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        
        # 连接信号 - 同时连接 stdout 和 stderr
        self._process.readyReadStandardOutput.connect(self._read_output)
        self._process.readyReadStandardError.connect(self._read_output)
        self._process.finished.connect(self._on_process_finished)
        
        # 启动 Shell
        if sys.platform == "win32":
            # Windows: 使用 PowerShell，设置 UTF-8 编码
            self._process.start("powershell.exe", [
                "-NoLogo",
                "-NoExit",
                "-Command",
                "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; $OutputEncoding = [System.Text.Encoding]::UTF8"
            ])
        else:
            # Linux/Mac: 使用 bash
            self._process.start("bash", ["-i"])
        
        if not self._process.waitForStarted(5000):
            self._output.appendPlainText("无法启动终端进程\n")
            self._status_label.setStyleSheet("color: #f14c4c; font-size: 10px;")
    
    def _read_output(self):
        """读取进程输出"""
        if not self._process:
            return
        
        # 读取所有可用数据
        while self._process.bytesAvailable() > 0:
            data = self._process.readAllStandardOutput()
            if data:
                # 尝试多种编码解码
                text = self._decode_text(bytes(data))
                # 处理 ANSI 转义序列
                text = self._process_ansi_codes(text)
                self._output.insertPlainText(text)
        
        # 滚动到底部
        scrollbar = self._output.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def _decode_text(self, data: bytes) -> str:
        """尝试多种编码解码文本"""
        # 尝试的编码列表
        encodings = ['utf-8', 'gbk', 'gb2312', 'cp936', 'latin-1']
        
        for encoding in encodings:
            try:
                return data.decode(encoding, errors='strict')
            except (UnicodeDecodeError, LookupError):
                continue
        
        # 如果所有编码都失败，使用 utf-8 并替换错误字符
        return data.decode('utf-8', errors='replace')
    
    def _process_ansi_codes(self, text: str) -> str:
        """处理 ANSI 转义序列"""
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)
    
    def _on_process_finished(self, exit_code, exit_status):
        """进程结束"""
        self._output.appendPlainText(f"\n[进程已结束，退出码: {exit_code}]\n")
        self._status_label.setStyleSheet("color: #f14c4c; font-size: 10px;")
    
    def _clear_terminal(self):
        """清空终端"""
        self._output.clear()
    
    def execute_command(self, command: str):
        """执行命令"""
        if self._process and self._process.state() == QProcess.ProcessState.Running:
            self._process.write((command + "\n").encode('utf-8'))
    
    def execute_code(self, code: str, temp_file=None):
        """执行代码"""
        # 使用项目自带的 Python 解释器
        python_exe = os.path.join(os.getcwd(), "python", "python.exe")
        if not os.path.exists(python_exe):
            # 如果项目自带的 Python 不存在，使用系统 Python
            python_exe = "python"
        
        if temp_file:
            # 使用 & 调用操作符，避免引号问题
            self.execute_command(f'& "{python_exe}" "{temp_file}"')
        else:
            import shlex
            self.execute_command(f'& "{python_exe}" -c {shlex.quote(code)}')
    
    def closeEvent(self, event):
        """关闭事件"""
        if self._process and self._process.state() != QProcess.ProcessState.NotRunning:
            self._process.terminate()
            self._process.waitForFinished(1000)
            self._process.kill()
        event.accept()
