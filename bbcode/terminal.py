# -*- coding: utf-8 -*-
"""
BBCode 嵌入式终端组件
提供沉浸式的 Python 交互体验 - 支持直接在终端输入
"""

import sys
import os
import re
from pathlib import Path
from typing import Optional, List

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit,
    QPushButton, QComboBox, QLabel, QFrame, QSplitter,
    QTabWidget, QToolButton, QMenu, QApplication, QScrollBar,
    QPlainTextEdit, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QProcess, QTimer, QSize
from PyQt6.QtGui import (
    QTextCursor, QFont, QColor, QKeyEvent, QAction,
    QFontMetrics, QPalette, QKeySequence
)
from PyQt6.QtCore import QProcessEnvironment


class TerminalWidget(QPlainTextEdit):
    """终端组件 - 支持直接输入"""
    
    # 信号
    command_entered = pyqtSignal(str)  # 用户输入命令
    interrupt_requested = pyqtSignal()  # 中断请求
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._prompt = ">>> "
        self._prompt_length = len(self._prompt)
        self._input_start_pos = 0
        self._history: List[str] = []
        self._history_index = 0
        
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI"""
        # 设置字体
        font = QFont("Consolas", 10)
        if not QFont(font).exactMatch():
            font = QFont("Courier New", 10)
        if not QFont(font).exactMatch():
            font = QFont("Monospace", 10)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        
        # 设置样式 - 终端风格
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #0c0c0c;
                color: #cccccc;
                border: none;
                selection-background-color: #264f78;
                selection-color: #ffffff;
                padding: 8px;
            }
        """)
        
        # 设置光标
        self.setCursorWidth(2)
        
        # 禁用自动换行
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        
        # 启用编辑（支持输入）
        self.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextEditable |
            Qt.TextInteractionFlag.TextSelectableByMouse |
            Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        
        # 设置滚动条样式
        self._setup_scrollbar()
    
    def _setup_scrollbar(self):
        """设置滚动条样式"""
        self.verticalScrollBar().setStyleSheet("""
            QScrollBar:vertical {
                background-color: #0c0c0c;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #424242;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #4f4f4f;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
    
    def append_output(self, text: str, color: str = "#cccccc"):
        """追加输出文本"""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        # 处理 ANSI 转义序列
        text = self._process_ansi_codes(text)
        
        # 设置文本颜色
        format = cursor.charFormat()
        format.setForeground(QColor(color))
        cursor.setCharFormat(format)
        
        cursor.insertText(text)
        
        # 更新输入起始位置
        self._input_start_pos = self.textCursor().position()
        
        # 滚动到底部
        self.scroll_to_bottom()
    
    def insert_prompt(self, prompt: str = ">>> "):
        """插入提示符"""
        self._prompt = prompt
        self._prompt_length = len(prompt)
        
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        # 设置提示符颜色
        format = cursor.charFormat()
        format.setForeground(QColor("#569cd6"))
        cursor.setCharFormat(format)
        
        cursor.insertText(prompt)
        
        # 记录输入起始位置
        self._input_start_pos = cursor.position()
        
        self.scroll_to_bottom()
    
    def _process_ansi_codes(self, text: str) -> str:
        """处理 ANSI 转义序列"""
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)
    
    def scroll_to_bottom(self):
        """滚动到底部"""
        scrollbar = self.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def get_current_input(self) -> str:
        """获取当前输入"""
        # 创建选择从输入起始位置到末尾
        temp_cursor = QTextCursor(self.document())
        temp_cursor.setPosition(self._input_start_pos)
        temp_cursor.movePosition(
            QTextCursor.MoveOperation.End,
            QTextCursor.MoveMode.KeepAnchor
        )
        return temp_cursor.selectedText()
    
    def clear_input(self):
        """清除当前输入"""
        cursor = self.textCursor()
        cursor.setPosition(self._input_start_pos)
        cursor.movePosition(
            QTextCursor.MoveOperation.End,
            QTextCursor.MoveMode.KeepAnchor
        )
        cursor.removeSelectedText()
    
    def keyPressEvent(self, event: QKeyEvent):
        """处理键盘事件"""
        key = event.key()
        modifiers = event.modifiers()
        
        # 检查光标位置
        cursor = self.textCursor()
        current_pos = cursor.position()
        
        # 如果光标在提示符之前，移动到最后
        if current_pos < self._input_start_pos:
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.setTextCursor(cursor)
            return
        
        # Enter - 执行命令
        if key == Qt.Key.Key_Return or key == Qt.Key.Key_Enter:
            if not (modifiers & Qt.KeyboardModifier.ShiftModifier):
                self._execute_current_line()
                return
        
        # Backspace - 防止删除提示符
        if key == Qt.Key.Key_Backspace:
            if current_pos <= self._input_start_pos:
                return
        
        # Delete - 防止删除提示符
        if key == Qt.Key.Key_Delete:
            if current_pos < self._input_start_pos:
                return
        
        # Up - 历史记录上一条
        if key == Qt.Key.Key_Up:
            if self._history and self._history_index > 0:
                self._history_index -= 1
                self.clear_input()
                cursor = self.textCursor()
                cursor.insertText(self._history[self._history_index])
            return
        
        # Down - 历史记录下一条
        if key == Qt.Key.Key_Down:
            if self._history and self._history_index < len(self._history) - 1:
                self._history_index += 1
                self.clear_input()
                cursor = self.textCursor()
                cursor.insertText(self._history[self._history_index])
            elif self._history_index >= len(self._history) - 1:
                self._history_index = len(self._history)
                self.clear_input()
            return
        
        # Home - 移动到输入起始位置
        if key == Qt.Key.Key_Home:
            cursor.setPosition(self._input_start_pos)
            self.setTextCursor(cursor)
            return
        
        # Ctrl+C - 复制或中断
        if key == Qt.Key.Key_C and modifiers == Qt.KeyboardModifier.ControlModifier:
            if cursor.hasSelection():
                self.copy()
            else:
                self.interrupt_requested.emit()
            return
        
        # Ctrl+V - 粘贴
        if key == Qt.Key.Key_V and modifiers == Qt.KeyboardModifier.ControlModifier:
            self.paste()
            return
        
        # Ctrl+A - 全选（仅选择输入区域）
        if key == Qt.Key.Key_A and modifiers == Qt.KeyboardModifier.ControlModifier:
            cursor.setPosition(self._input_start_pos)
            cursor.movePosition(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.KeepAnchor)
            self.setTextCursor(cursor)
            return
        
        # 默认处理
        super().keyPressEvent(event)
    
    def _execute_current_line(self):
        """执行当前行"""
        input_text = self.get_current_input()
        if not input_text.strip():
            self.append_output("\n")
            self.insert_prompt()
            return
        
        # 添加到历史
        if not self._history or input_text != self._history[-1]:
            self._history.append(input_text)
        self._history_index = len(self._history)
        
        # 显示换行并发送信号
        self.append_output("\n")
        self.command_entered.emit(input_text)
    
    def contextMenuEvent(self, event):
        """右键菜单"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #3c3c3c;
                color: #d4d4d4;
                border: 1px solid #555;
            }
            QMenu::item {
                padding: 5px 20px;
            }
            QMenu::item:selected {
                background-color: #094771;
            }
        """)
        
        # 复制
        copy_action = QAction("复制", self)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.triggered.connect(self.copy)
        copy_action.setEnabled(self.textCursor().hasSelection())
        menu.addAction(copy_action)
        
        # 粘贴
        paste_action = QAction("粘贴", self)
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.triggered.connect(self.paste)
        menu.addAction(paste_action)
        
        menu.addSeparator()
        
        # 全选
        select_all_action = QAction("全选", self)
        select_all_action.setShortcut(QKeySequence.StandardKey.SelectAll)
        select_all_action.triggered.connect(self.selectAll)
        menu.addAction(select_all_action)
        
        menu.addSeparator()
        
        # 清空终端
        clear_action = QAction("清空终端", self)
        clear_action.triggered.connect(self.clear)
        menu.addAction(clear_action)
        
        menu.exec(event.globalPos())


class Terminal(QWidget):
    """终端组件 - 嵌入式 Python 终端"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._process: Optional[QProcess] = None
        
        self._setup_ui()
        self._start_python_process()
    
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
        title_label = QLabel("Python")
        title_label.setStyleSheet("color: #cccccc; font-size: 12px; font-weight: bold;")
        toolbar_layout.addWidget(title_label)
        
        # 状态指示器
        self._status_label = QLabel("●")
        self._status_label.setStyleSheet("color: #0dbc79; font-size: 10px;")
        self._status_label.setToolTip("运行中")
        toolbar_layout.addWidget(self._status_label)
        
        toolbar_layout.addStretch()
        
        # 重启按钮
        restart_btn = QToolButton()
        restart_btn.setText("🔄")
        restart_btn.setToolTip("重启终端")
        restart_btn.setStyleSheet("""
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
        restart_btn.clicked.connect(self._restart_process)
        toolbar_layout.addWidget(restart_btn)
        
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
        
        # 终端显示区域（支持直接输入）
        self._terminal = TerminalWidget()
        self._terminal.command_entered.connect(self._on_command_entered)
        self._terminal.interrupt_requested.connect(self._on_interrupt)
        layout.addWidget(self._terminal, stretch=1)
    
    def _start_python_process(self):
        """启动 PowerShell 进程作为终端"""
        self._process = QProcess(self)
        self._process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        
        # 设置环境变量 - 确保 UTF-8 编码
        env = QProcessEnvironment.systemEnvironment()
        env.insert("PYTHONIOENCODING", "utf-8")
        env.insert("PYTHONUTF8", "1")
        # Windows 下设置代码页为 UTF-8
        if sys.platform == "win32":
            env.insert("CHCP", "65001")
        self._process.setProcessEnvironment(env)
        
        # 连接信号
        self._process.readyReadStandardOutput.connect(self._read_output)
        self._process.readyReadStandardError.connect(self._read_error)
        self._process.finished.connect(self._on_process_finished)
        self._process.started.connect(self._on_process_started)
        
        # 启动 PowerShell (Windows) 或 bash (Linux/Mac)
        if sys.platform == "win32":
            # 使用 PowerShell
            self._process.start("powershell.exe", ["-NoLogo", "-NoExit", "-Command", "chcp 65001"])
        else:
            # 使用 bash
            self._process.start("bash", ["-i"])
        
        if not self._process.waitForStarted(5000):
            self._terminal.append_output("无法启动终端进程\n", "#f14c4c")
            self._status_label.setStyleSheet("color: #f14c4c; font-size: 10px;")
            self._status_label.setToolTip("未运行")
    
    def _on_process_started(self):
        """进程启动完成"""
        self._terminal.append_output("BBCode Terminal\n", "#d4d4d4")
        self._terminal.append_output('Type commands to execute. Use "python" to run Python.\n\n', "#888888")
        self._terminal.insert_prompt("PS> ")
    
    def _read_output(self):
        """读取标准输出"""
        data = self._process.readAllStandardOutput()
        text = bytes(data).decode('utf-8', errors='replace')
        
        if text:
            # 移除 PowerShell 提示符
            text = text.replace("PS ", "").replace(">>> ", "").replace("... ", "")
            if text.strip():
                self._terminal.append_output(text, "#d4d4d4")
    
    def _read_error(self):
        """读取标准错误"""
        data = self._process.readAllStandardError()
        text = bytes(data).decode('utf-8', errors='replace')
        if text:
            self._terminal.append_output(text, "#f14c4c")
    
    def _on_process_finished(self, exit_code, exit_status):
        """进程结束"""
        self._terminal.append_output(f"\n[进程已结束，退出码: {exit_code}]\n", "#666666")
        self._status_label.setStyleSheet("color: #f14c4c; font-size: 10px;")
        self._status_label.setToolTip("已停止")
    
    def _on_command_entered(self, command: str):
        """处理输入的命令"""
        if not command.strip():
            self._terminal.insert_prompt("PS> ")
            return
        
        # 发送到终端进程
        if self._process and self._process.state() == QProcess.ProcessState.Running:
            self._process.write((command + "\n").encode('utf-8'))
        else:
            self._terminal.append_output("终端进程未运行\n", "#f14c4c")
            self._terminal.insert_prompt("PS> ")
    
    def _on_interrupt(self):
        """处理中断请求"""
        if self._process and self._process.state() == QProcess.ProcessState.Running:
            self._process.write(b"\x03")
        self._terminal.insert_prompt("PS> ")
    
    def _clear_terminal(self):
        """清空终端"""
        self._terminal.clear()
        self._terminal.append_output("BBCode Terminal\n", "#d4d4d4")
        self._terminal.append_output('Type commands to execute. Use "python" to run Python.\n\n', "#888888")
        self._terminal.insert_prompt("PS> ")
    
    def _restart_process(self):
        """重启进程"""
        if self._process and self._process.state() != QProcess.ProcessState.NotRunning:
            self._process.terminate()
            self._process.waitForFinished(1000)
            self._process.kill()
        
        self._terminal.clear()
        self._terminal._history.clear()
        self._terminal._history_index = 0
        
        self._start_python_process()
    
    def execute_code(self, code: str, temp_file: Optional[str] = None):
        """执行代码（从编辑器调用）- 保存到临时文件并运行
        
        Args:
            code: 要执行的代码
            temp_file: 指定的临时文件路径，如果为None则自动创建
        """
        if not code.strip():
            return
        
        # 显示执行标记
        self._terminal.append_output("\n[运行代码]\n", "#0dbc79")
        
        # 清理代码
        code = code.replace('\x03', '').strip()
        
        # 获取工作目录
        work_dir = os.path.dirname(os.path.dirname(__file__))
        
        # 如果没有指定临时文件，在 demo 文件夹中创建
        if temp_file is None:
            demo_dir = os.path.join(work_dir, "demo")
            os.makedirs(demo_dir, exist_ok=True)
            for i in range(1, 100):
                candidate = os.path.join(demo_dir, f"demo{i}.py")
                if not os.path.exists(candidate):
                    temp_file = candidate
                    break
        
        if not temp_file:
            self._terminal.append_output("无法创建临时文件\n", "#f14c4c")
            return
        
        # 保存代码到临时文件
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(code)
        except Exception as e:
            self._terminal.append_output(f"保存代码失败: {e}\n", "#f14c4c")
            return
        
        # 获取文件名（用于显示）
        temp_filename = os.path.basename(temp_file)
        
        # 显示执行的文件
        self._terminal.append_output(f">>> python {temp_filename}\n", "#569cd6")
        
        if self._process and self._process.state() == QProcess.ProcessState.Running:
            # 在终端中运行 Python 文件
            # 使用内置的 python/python.exe
            python_exe = os.path.join(work_dir, "python", "python.exe")
            if not os.path.exists(python_exe):
                python_exe = "python"
            
            # 发送运行命令到终端 - 使用 UTF-8 编码
            # 使用正斜杠避免转义问题
            python_exe_forward = python_exe.replace("\\", "/")
            temp_file_forward = temp_file.replace("\\", "/")
            run_cmd = f'& "{python_exe_forward}" "{temp_file_forward}"\n'
            self._process.write(run_cmd.encode('utf-8'))
        else:
            self._terminal.append_output("终端未运行\n", "#f14c4c")
            self._terminal.insert_prompt("PS> ")
        
        return temp_file
    
    def clear_demo_folder(self):
        """清空 demo 文件夹中的所有 .py 文件"""
        try:
            work_dir = os.path.dirname(os.path.dirname(__file__))
            demo_dir = os.path.join(work_dir, "demo")
            if os.path.exists(demo_dir):
                for file in os.listdir(demo_dir):
                    if file.endswith('.py'):
                        file_path = os.path.join(demo_dir, file)
                        try:
                            os.remove(file_path)
                        except Exception:
                            pass
        except Exception:
            pass
    
    def closeEvent(self, event):
        """关闭事件"""
        # 清空 demo 文件夹
        self.clear_demo_folder()
        
        if self._process and self._process.state() != QProcess.ProcessState.NotRunning:
            self._process.terminate()
            self._process.waitForFinished(1000)
            self._process.kill()
        event.accept()
