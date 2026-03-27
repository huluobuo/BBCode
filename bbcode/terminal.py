# -*- coding: utf-8 -*-
"""
BBCode 终端组件
支持 Python Shell 和系统命令
"""

import sys
import subprocess
import queue
from typing import Optional
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QComboBox, QLabel
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QTextCursor, QFont, QColor, QKeyEvent


class TerminalWidget(QTextEdit):
    """终端显示组件"""
    
    command_entered = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setReadOnly(True)
        self.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        
        font = QFont("Consolas", 10)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        
        self._prompt = ">>> "
        self._current_input = ""
        self._history: list = []
        self._history_index = 0
        
        self.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: none;
            }
        """)
    
    def append_output(self, text: str, color: str = "#d4d4d4"):
        """追加输出文本"""
        self.moveCursor(QTextCursor.MoveOperation.End)
        self.setTextColor(QColor(color))
        self.insertPlainText(text)
        self.moveCursor(QTextCursor.MoveOperation.End)
    
    def append_prompt(self):
        """显示提示符"""
        self.append_output(self._prompt, "#569cd6")
    
    def keyPressEvent(self, event: QKeyEvent):
        """处理键盘输入"""
        if not self.isReadOnly():
            super().keyPressEvent(event)
            return
        
        key = event.key()
        
        if key == Qt.Key.Key_Return or key == Qt.Key.Key_Enter:
            self._execute_current_input()
        elif key == Qt.Key.Key_Backspace:
            if self._current_input:
                self._current_input = self._current_input[:-1]
                self._update_display()
        elif key == Qt.Key.Key_Up:
            self._navigate_history(-1)
        elif key == Qt.Key.Key_Down:
            self._navigate_history(1)
        elif not event.text().isControl():
            self._current_input += event.text()
            self._update_display()
    
    def _execute_current_input(self):
        """执行当前输入"""
        if self._current_input.strip():
            self._history.append(self._current_input)
            self._history_index = len(self._history)
            self.append_output("\n")
            self.command_entered.emit(self._current_input)
        else:
            self.append_output("\n")
            self.append_prompt()
        self._current_input = ""
    
    def _update_display(self):
        """更新显示"""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine, QTextCursor.MoveMode.KeepAnchor)
        cursor.removeSelectedText()
        self.append_output(self._prompt + self._current_input)
    
    def _navigate_history(self, direction: int):
        """导航历史记录"""
        if not self._history:
            return
        
        self._history_index += direction
        self._history_index = max(0, min(self._history_index, len(self._history)))
        
        if self._history_index < len(self._history):
            self._current_input = self._history[self._history_index]
        else:
            self._current_input = ""
        
        self._update_display()


class PythonInterpreter(QThread):
    """Python 解释器线程"""
    output_ready = pyqtSignal(str)
    error_ready = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self._command_queue = queue.Queue()
        self._running = True
        self._globals = {"__name__": "__console__", "__doc__": None}
    
    def run(self):
        """运行解释器循环"""
        while self._running:
            try:
                command = self._command_queue.get(timeout=0.1)
                self._execute_command(command)
            except queue.Empty:
                continue
    
    def _execute_command(self, command: str):
        """执行命令"""
        try:
            try:
                result = eval(command, self._globals)
                if result is not None:
                    self.output_ready.emit(repr(result) + "\n")
            except SyntaxError:
                exec(command, self._globals)
        except Exception as e:
            self.error_ready.emit(f"{type(e).__name__}: {e}\n")
    
    def execute(self, command: str):
        """提交命令执行"""
        self._command_queue.put(command)
    
    def stop(self):
        """停止解释器"""
        self._running = False


class Terminal(QWidget):
    """终端组件 - 支持 Python 和系统命令"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._setup_ui()
        self._python_interpreter: Optional[PythonInterpreter] = None
        self._current_mode = "python"
        
        self._start_python_interpreter()
    
    def _setup_ui(self):
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
        
        clear_btn = QPushButton("清空")
        clear_btn.clicked.connect(self._clear_terminal)
        toolbar.addWidget(clear_btn)
        
        layout.addLayout(toolbar)
        
        # 终端显示
        self._terminal = TerminalWidget()
        self._terminal.command_entered.connect(self._on_command_entered)
        layout.addWidget(self._terminal)
        
        # 欢迎信息
        self._terminal.append_output("BBCode Python Shell\n")
        self._terminal.append_output(f"Python {sys.version}\n\n")
        self._terminal.append_prompt()
    
    def _start_python_interpreter(self):
        """启动 Python 解释器"""
        self._python_interpreter = PythonInterpreter()
        self._python_interpreter.output_ready.connect(self._on_python_output)
        self._python_interpreter.error_ready.connect(self._on_python_error)
        self._python_interpreter.start()
    
    def _on_mode_changed(self, mode: str):
        """模式切换"""
        self._current_mode = "python" if mode == "Python" else "system"
        self._terminal.append_output(f"\n[切换到 {mode} 模式]\n")
        self._terminal.append_prompt()
    
    def _on_command_entered(self, command: str):
        """处理输入的命令"""
        if self._current_mode == "python":
            self._python_interpreter.execute(command)
        else:
            self._execute_system_command(command)
    
    def _execute_system_command(self, command: str):
        """执行系统命令"""
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=30
            )
            if result.stdout:
                self._terminal.append_output(result.stdout, "#d4d4d4")
            if result.stderr:
                self._terminal.append_output(result.stderr, "#ff6b6b")
        except Exception as e:
            self._terminal.append_output(f"Error: {e}\n", "#ff6b6b")
        
        self._terminal.append_prompt()
    
    def _on_python_output(self, output: str):
        """Python 输出处理"""
        self._terminal.append_output(output, "#d4d4d4")
        self._terminal.append_prompt()
    
    def _on_python_error(self, error: str):
        """Python 错误处理"""
        self._terminal.append_output(error, "#ff6b6b")
        self._terminal.append_prompt()
    
    def _clear_terminal(self):
        """清空终端"""
        self._terminal.clear()
        self._terminal.append_output("BBCode Python Shell\n\n")
        self._terminal.append_prompt()
    
    def closeEvent(self, event):
        """关闭事件"""
        if self._python_interpreter:
            self._python_interpreter.stop()
            self._python_interpreter.wait()
        event.accept()
