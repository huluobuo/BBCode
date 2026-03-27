# -*- coding: utf-8 -*-
"""
BBCode PyQt6 终端组件
基于 PyQt6 的现代化 Python Shell 终端
"""

import sys
import os
import re
import code
import traceback
from io import StringIO
from typing import Optional, List, Callable, Dict, Any
from enum import Enum

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit,
    QPushButton, QLabel, QFrame, QScrollArea, QSizePolicy,
    QApplication, QMenu, QToolButton, QSplitter, QComboBox,
    QPlainTextEdit
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QSize, QProcess
from PyQt6.QtGui import QTextCursor, QTextCharFormat, QColor, QFont, QKeyEvent

from thonny.qt_themes import get_theme_manager


class TerminalMode(Enum):
    """终端模式"""
    PYTHON_SHELL = "python"
    SYSTEM_SHELL = "system"
    MICROPYTHON = "micropython"


class PythonInterpreter(QThread):
    """Python 解释器线程"""
    
    output_ready = pyqtSignal(str)
    error_ready = pyqtSignal(str)
    execution_finished = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self._locals: Dict[str, Any] = {}
        self._command_queue: List[str] = []
        self._running = False
        
        # 初始化全局命名空间
        self._locals['__name__'] = '__console__'
        self._locals['__doc__'] = None
    
    def run(self):
        """运行解释器循环"""
        self._running = True
        
        while self._running:
            if self._command_queue:
                command = self._command_queue.pop(0)
                self._execute_command(command)
            else:
                self.msleep(10)
    
    def _execute_command(self, command: str):
        """执行命令"""
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        
        stdout_buffer = StringIO()
        stderr_buffer = StringIO()
        
        sys.stdout = stdout_buffer
        sys.stderr = stderr_buffer
        
        try:
            # 尝试作为表达式求值
            try:
                result = eval(command, self._locals)
                if result is not None:
                    print(repr(result))
            except SyntaxError:
                # 作为语句执行
                exec(command, self._locals)
        except Exception as e:
            traceback.print_exc()
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
        
        # 发送输出
        output = stdout_buffer.getvalue()
        error = stderr_buffer.getvalue()
        
        if output:
            self.output_ready.emit(output)
        if error:
            self.error_ready.emit(error)
        
        self.execution_finished.emit()
    
    def execute(self, command: str):
        """添加命令到队列"""
        self._command_queue.append(command)
    
    def stop(self):
        """停止解释器"""
        self._running = False
        self.wait(1000)


class TerminalWidget(QFrame):
    """终端组件"""
    
    command_executed = pyqtSignal(str, str)  # command, output
    mode_changed = pyqtSignal(TerminalMode)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._mode = TerminalMode.PYTHON_SHELL
        self._history: List[str] = []
        self._history_index = 0
        self._current_prompt = ">>> "
        self._interpreter: Optional[PythonInterpreter] = None
        self._setup_ui()
        self._setup_interpreter()
    
    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 工具栏
        toolbar = QFrame()
        toolbar.setFixedHeight(36)
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(8, 4, 8, 4)
        toolbar_layout.setSpacing(8)
        
        # 模式选择
        mode_label = QLabel("模式:")
        toolbar_layout.addWidget(mode_label)
        
        self._mode_combo = QComboBox()
        self._mode_combo.addItems(["Python Shell", "系统终端", "MicroPython"])
        self._mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        self._mode_combo.setFixedWidth(150)
        self._mode_combo.setFixedHeight(24)
        toolbar_layout.addWidget(self._mode_combo)
        
        toolbar_layout.addStretch()
        
        # 清除按钮
        clear_btn = QPushButton("清除")
        clear_btn.setFixedHeight(24)
        clear_btn.clicked.connect(self.clear)
        toolbar_layout.addWidget(clear_btn)
        
        # 停止按钮
        self._stop_btn = QPushButton("停止")
        self._stop_btn.setFixedHeight(24)
        self._stop_btn.setEnabled(False)
        self._stop_btn.clicked.connect(self._stop_execution)
        toolbar_layout.addWidget(self._stop_btn)
        
        layout.addWidget(toolbar)
        
        # 终端显示区域
        self._terminal = QPlainTextEdit()
        self._terminal.setReadOnly(False)
        self._terminal.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        
        # 设置等宽字体
        font = QFont("Consolas", 11)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self._terminal.setFont(font)
        
        # 设置颜色
        theme = get_theme_manager().get_colors()
        self._terminal.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {theme.bg_secondary};
                color: {theme.text_primary};
                border: none;
                padding: 8px;
            }}
        """)
        
        layout.addWidget(self._terminal)
        
        # 连接键盘事件
        self._terminal.installEventFilter(self)
        
        # 显示欢迎信息
        self._show_welcome()
        self._insert_prompt()
    
    def _setup_interpreter(self):
        """设置解释器"""
        self._interpreter = PythonInterpreter()
        self._interpreter.output_ready.connect(self._on_output)
        self._interpreter.error_ready.connect(self._on_error)
        self._interpreter.execution_finished.connect(self._on_execution_finished)
        self._interpreter.start()
    
    def _show_welcome(self):
        """显示欢迎信息"""
        welcome = """Python 3.11.0 (default, Nov  1 2022, 10:00:00) [MSC v.1933 64 bit (AMD64)] :: Anaconda, Inc. on win32
Type "help", "copyright", "credits" or "license" for more information.
"""
        self._terminal.appendPlainText(welcome)
    
    def _insert_prompt(self):
        """插入提示符"""
        self._terminal.appendPlainText(self._current_prompt)
        self._scroll_to_bottom()
    
    def _get_current_line(self) -> str:
        """获取当前行文本"""
        cursor = self._terminal.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
        cursor.movePosition(QTextCursor.MoveOperation.EndOfLine, QTextCursor.MoveMode.KeepAnchor)
        line = cursor.selectedText()
        
        # 去掉提示符
        if line.startswith(self._current_prompt):
            line = line[len(self._current_prompt):]
        
        return line
    
    def _replace_current_line(self, text: str):
        """替换当前行"""
        cursor = self._terminal.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
        cursor.movePosition(QTextCursor.MoveOperation.EndOfLine, QTextCursor.MoveMode.KeepAnchor)
        cursor.removeSelectedText()
        cursor.insertText(self._current_prompt + text)
    
    def _scroll_to_bottom(self):
        """滚动到底部"""
        scrollbar = self._terminal.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def eventFilter(self, obj, event):
        """事件过滤器"""
        if obj == self._terminal and event.type() == event.Type.KeyPress:
            # event 已经是 QKeyEvent 类型，直接使用
            key_event = event

            if key_event.key() == Qt.Key.Key_Return:
                self._handle_return()
                return True
            
            elif key_event.key() == Qt.Key.Key_Up:
                self._handle_up()
                return True
            
            elif key_event.key() == Qt.Key.Key_Down:
                self._handle_down()
                return True
            
            elif key_event.key() == Qt.Key.Key_Left:
                # 防止光标移动到提示符之前
                cursor = self._terminal.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
                line_start = cursor.position()
                if self._terminal.textCursor().position() <= line_start + len(self._current_prompt):
                    return True
            
            elif key_event.key() == Qt.Key.Key_Backspace:
                # 防止删除提示符
                cursor = self._terminal.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
                line_start = cursor.position()
                if self._terminal.textCursor().position() <= line_start + len(self._current_prompt):
                    return True
            
            elif key_event.key() == Qt.Key.Key_Home:
                # Home 键移动到提示符之后
                cursor = self._terminal.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
                cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.MoveAnchor, len(self._current_prompt))
                self._terminal.setTextCursor(cursor)
                return True
        
        return super().eventFilter(obj, event)
    
    def _handle_return(self):
        """处理回车键"""
        command = self._get_current_line()
        
        # 添加到历史
        if command.strip():
            self._history.append(command)
            self._history_index = len(self._history)
        
        # 执行命令
        self._terminal.appendPlainText("")
        
        if self._mode == TerminalMode.PYTHON_SHELL:
            self._execute_python_command(command)
        else:
            self._execute_system_command(command)
    
    def _handle_up(self):
        """处理上箭头"""
        if self._history_index > 0:
            self._history_index -= 1
            self._replace_current_line(self._history[self._history_index])
    
    def _handle_down(self):
        """处理下箭头"""
        if self._history_index < len(self._history) - 1:
            self._history_index += 1
            self._replace_current_line(self._history[self._history_index])
        elif self._history_index == len(self._history) - 1:
            self._history_index += 1
            self._replace_current_line("")
    
    def _execute_python_command(self, command: str):
        """执行 Python 命令"""
        if not command.strip():
            self._insert_prompt()
            return
        
        self._stop_btn.setEnabled(True)
        self._interpreter.execute(command)
    
    def _execute_system_command(self, command: str):
        """执行系统命令"""
        if not command.strip():
            self._insert_prompt()
            return
        
        self._stop_btn.setEnabled(True)
        
        # 创建进程执行命令
        self._process = QProcess(self)
        self._process.readyReadStandardOutput.connect(self._on_process_output)
        self._process.readyReadStandardError.connect(self._on_process_error)
        self._process.finished.connect(self._on_process_finished)
        
        if os.name == 'nt':
            self._process.start("cmd", ["/c", command])
        else:
            self._process.start("bash", ["-c", command])
    
    def _on_output(self, output: str):
        """处理输出"""
        self._terminal.appendPlainText(output.rstrip())
        self._scroll_to_bottom()
    
    def _on_error(self, error: str):
        """处理错误"""
        theme = get_theme_manager().get_colors()
        
        # 设置错误颜色
        cursor = self._terminal.textCursor()
        format = QTextCharFormat()
        format.setForeground(QColor(theme.error))
        cursor.setCharFormat(format)
        
        self._terminal.appendPlainText(error.rstrip())
        
        # 恢复默认格式
        format.setForeground(QColor(theme.text_primary))
        cursor.setCharFormat(format)
        
        self._scroll_to_bottom()
    
    def _on_execution_finished(self):
        """执行完成"""
        self._stop_btn.setEnabled(False)
        self._insert_prompt()
    
    def _on_process_output(self):
        """处理进程输出"""
        output = self._process.readAllStandardOutput().data().decode('utf-8', errors='ignore')
        self._terminal.appendPlainText(output.rstrip())
        self._scroll_to_bottom()
    
    def _on_process_error(self):
        """处理进程错误"""
        error = self._process.readAllStandardError().data().decode('utf-8', errors='ignore')
        theme = get_theme_manager().get_colors()
        
        cursor = self._terminal.textCursor()
        format = QTextCharFormat()
        format.setForeground(QColor(theme.error))
        cursor.setCharFormat(format)
        
        self._terminal.appendPlainText(error.rstrip())
        
        format.setForeground(QColor(theme.text_primary))
        cursor.setCharFormat(format)
        
        self._scroll_to_bottom()
    
    def _on_process_finished(self):
        """进程结束"""
        self._stop_btn.setEnabled(False)
        self._insert_prompt()
    
    def _on_mode_changed(self, index: int):
        """模式改变"""
        modes = [TerminalMode.PYTHON_SHELL, TerminalMode.SYSTEM_SHELL, TerminalMode.MICROPYTHON]
        self._mode = modes[index]
        
        if self._mode == TerminalMode.PYTHON_SHELL:
            self._current_prompt = ">>> "
        else:
            self._current_prompt = "$ "
        
        self.mode_changed.emit(self._mode)
        self._insert_prompt()
    
    def _stop_execution(self):
        """停止执行"""
        if self._mode == TerminalMode.PYTHON_SHELL:
            # Python 解释器不支持中断
            pass
        else:
            if hasattr(self, '_process') and self._process:
                self._process.terminate()
        
        self._stop_btn.setEnabled(False)
    
    def clear(self):
        """清除终端"""
        self._terminal.clear()
        self._show_welcome()
        self._insert_prompt()
    
    def write(self, text: str):
        """写入文本"""
        self._terminal.appendPlainText(text)
        self._scroll_to_bottom()
    
    def write_error(self, text: str):
        """写入错误文本"""
        theme = get_theme_manager().get_colors()
        
        cursor = self._terminal.textCursor()
        format = QTextCharFormat()
        format.setForeground(QColor(theme.error))
        cursor.setCharFormat(format)
        
        self._terminal.appendPlainText(text)
        
        format.setForeground(QColor(theme.text_primary))
        cursor.setCharFormat(format)
        
        self._scroll_to_bottom()
    
    def set_mode(self, mode: TerminalMode):
        """设置模式"""
        self._mode = mode
        
        if mode == TerminalMode.PYTHON_SHELL:
            self._mode_combo.setCurrentIndex(0)
        elif mode == TerminalMode.SYSTEM_SHELL:
            self._mode_combo.setCurrentIndex(1)
        else:
            self._mode_combo.setCurrentIndex(2)
    
    def get_mode(self) -> TerminalMode:
        """获取当前模式"""
        return self._mode
    
    def closeEvent(self, event):
        """关闭事件"""
        if self._interpreter:
            self._interpreter.stop()
        super().closeEvent(event)


class TerminalDockWidget(QWidget):
    """终端停靠窗口"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建终端组件
        self._terminal = TerminalWidget()
        layout.addWidget(self._terminal)
    
    def get_terminal(self) -> TerminalWidget:
        """获取终端组件"""
        return self._terminal


# 测试代码
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    from thonny.qt_themes import apply_theme
    
    app = QApplication(sys.argv)
    apply_theme(app, "dark")
    
    window = TerminalWidget()
    window.resize(800, 400)
    window.show()
    
    sys.exit(app.exec())
