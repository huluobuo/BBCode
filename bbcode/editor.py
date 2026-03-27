# -*- coding: utf-8 -*-
"""
BBCode 代码编辑器组件
整合：行号显示、语法高亮、语法检查
"""

import re
import sys
import subprocess
from typing import Optional, List, Tuple
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit, QTextEdit,
    QLabel, QFrame, QApplication, QTabWidget, QFileDialog, QMessageBox,
    QSplitter, QTreeView, QDockWidget, QMainWindow, QMenuBar, QMenu,
    QToolBar, QStatusBar, QPushButton, QComboBox, QLineEdit, QToolButton,
    QSizePolicy, QProgressBar
)
from PyQt6.QtCore import Qt, QRect, pyqtSignal, QTimer, QSettings, QThread
from PyQt6.QtGui import (
    QFont, QColor, QPainter, QTextFormat, QTextCharFormat,
    QSyntaxHighlighter, QTextCursor, QTextDocument, QKeyEvent,
    QAction, QIcon, QKeySequence, QCloseEvent, QFileSystemModel
)


# ============== 语法高亮 ==============
class PythonSyntaxHighlighter(QSyntaxHighlighter):
    """Python 语法高亮器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.colors = {
            'keyword': QColor("#569cd6"),
            'string': QColor("#ce9178"),
            'comment': QColor("#6a9955"),
            'function': QColor("#dcdcaa"),
            'number': QColor("#b5cea8"),
            'operator': QColor("#d4d4d4"),
            'builtin': QColor("#4ec9b0"),
            'class': QColor("#4ec9b0"),
        }
        
        self.keywords = [
            'and', 'as', 'assert', 'break', 'class', 'continue', 'def',
            'del', 'elif', 'else', 'except', 'False', 'finally', 'for',
            'from', 'global', 'if', 'import', 'in', 'is', 'lambda',
            'None', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return',
            'True', 'try', 'while', 'with', 'yield', 'async', 'await'
        ]
        
        self.builtins = [
            'abs', 'all', 'any', 'bin', 'bool', 'bytearray', 'bytes',
            'callable', 'chr', 'classmethod', 'compile', 'complex',
            'delattr', 'dict', 'dir', 'divmod', 'enumerate', 'eval',
            'exec', 'filter', 'float', 'format', 'frozenset', 'getattr',
            'globals', 'hasattr', 'hash', 'help', 'hex', 'id', 'input',
            'int', 'isinstance', 'issubclass', 'iter', 'len', 'list',
            'locals', 'map', 'max', 'memoryview', 'min', 'next', 'object',
            'oct', 'open', 'ord', 'pow', 'print', 'property', 'range',
            'repr', 'reversed', 'round', 'set', 'setattr', 'slice',
            'sorted', 'staticmethod', 'str', 'sum', 'super', 'tuple',
            'type', 'vars', 'zip', '__import__'
        ]
        
        self.rules = []
        self.rules.append((r'\b(' + '|'.join(self.keywords) + r')\b', self.colors['keyword']))
        self.rules.append((r'\b(' + '|'.join(self.builtins) + r')(?=\s*\()', self.colors['builtin']))
        self.rules.append((r'\b[A-Z][a-zA-Z0-9_]*\b', self.colors['class']))
        self.rules.append((r'\bdef\s+(\w+)', self.colors['function']))
        self.rules.append((r'\bclass\s+(\w+)', self.colors['class']))
        self.rules.append((r"'[^'\\]*(\\.[^'\\]*)*'", self.colors['string']))
        self.rules.append((r'"[^"\\]*(\\.[^"\\]*)*"', self.colors['string']))
        self.rules.append((r"'''[^']*'''", self.colors['string']))
        self.rules.append((r'"""[^"]*"""', self.colors['string']))
        self.rules.append((r'\b\d+\.?\d*\b', self.colors['number']))
        self.rules.append((r'#[^\n]*', self.colors['comment']))
        self.rules.append((r'[\+\-\*\/\%\=\<\>\!\&\|\^\~]', self.colors['operator']))
    
    def highlightBlock(self, text):
        for pattern, color in self.rules:
            expression = re.compile(pattern)
            for match in expression.finditer(text):
                start = match.start()
                end = match.end()
                if self._is_in_comment_or_string(text, start):
                    continue
                fmt = QTextCharFormat()
                fmt.setForeground(color)
                self.setFormat(start, end - start, fmt)
    
    def _is_in_comment_or_string(self, text, pos):
        comment_pos = text.find('#')
        if comment_pos != -1 and pos > comment_pos:
            return True
        return False


# ============== 行号区域 ==============
class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self._editor = editor
    
    def sizeHint(self):
        return self._editor.line_number_area_width()
    
    def paintEvent(self, event):
        self._editor.line_number_area_paint_event(event)


# ============== 代码编辑器 ==============
class CodeEditor(QPlainTextEdit):
    """代码编辑器 - 支持行号、语法高亮、语法检查"""
    
    syntax_error = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._file_path: Optional[str] = None
        self._is_modified = False
        self._syntax_error_line: Optional[int] = None
        
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        
        font = QFont("Consolas", 12)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        self.setTabStopDistance(40)
        
        self._line_number_area = LineNumberArea(self)
        
        self.blockCountChanged.connect(self._update_line_number_area_width)
        self.updateRequest.connect(self._update_line_number_area)
        self.cursorPositionChanged.connect(self._highlight_current_line)
        self.textChanged.connect(self._on_text_changed)
        
        self._update_line_number_area_width(0)
        
        self._highlighter = PythonSyntaxHighlighter(self.document())
        
        self._syntax_check_timer = QTimer(self)
        self._syntax_check_timer.timeout.connect(self._check_syntax)
        self._syntax_check_timer.setSingleShot(True)
        
        self._highlight_current_line()
    
    def line_number_area_width(self):
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1
        space = 10 + self.fontMetrics().horizontalAdvance('9') * digits
        return space
    
    def _update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)
    
    def _update_line_number_area(self, rect, dy):
        if dy:
            self._line_number_area.scroll(0, dy)
        else:
            self._line_number_area.update(0, rect.y(), self._line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self._update_line_number_area_width(0)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self._line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )
    
    def line_number_area_paint_event(self, event):
        painter = QPainter(self._line_number_area)
        painter.fillRect(event.rect(), QColor("#252526"))
        
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())
        
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor("#858585"))
                painter.drawText(
                    0, top, self._line_number_area.width() - 5,
                    self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight,
                    number
                )
            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            block_number += 1
    
    def _highlight_current_line(self):
        extra_selections = []
        
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor("#2d2d30")
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        
        if self._syntax_error_line is not None:
            error_selection = QTextEdit.ExtraSelection()
            error_color = QColor("#ff6b6b")
            error_selection.format.setUnderlineColor(error_color)
            error_selection.format.setUnderlineStyle(QTextCharFormat.UnderlineStyle.SpellCheckUnderline)
            error_selection.format.setBackground(QColor("#3d1f1f"))
            
            cursor = QTextCursor(self.document())
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            for _ in range(self._syntax_error_line - 1):
                cursor.movePosition(QTextCursor.MoveOperation.NextBlock)
            cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
            
            error_selection.cursor = cursor
            extra_selections.append(error_selection)
        
        self.setExtraSelections(extra_selections)
    
    def _on_text_changed(self):
        if not self._is_modified:
            self._is_modified = True
        self._syntax_check_timer.stop()
        self._syntax_check_timer.start(1000)
    
    def _check_syntax(self):
        code = self.toPlainText()
        if not code.strip():
            self._syntax_error_line = None
            self._highlight_current_line()
            self.syntax_error.emit("")
            return
        
        try:
            compile(code, '<string>', 'exec')
            self._syntax_error_line = None
            self._highlight_current_line()
            self.syntax_error.emit("")
        except SyntaxError as e:
            error_msg = f"语法错误 (行 {e.lineno}): {e.msg}"
            self._syntax_error_line = e.lineno
            self._highlight_current_line()
            self.syntax_error.emit(error_msg)
        except Exception as e:
            self._syntax_error_line = None
            self._highlight_current_line()
            self.syntax_error.emit(f"错误: {str(e)}")
    
    def get_file_path(self) -> Optional[str]:
        return self._file_path
    
    def set_file_path(self, path: str):
        self._file_path = path
    
    def is_modified(self) -> bool:
        return self._is_modified
    
    def set_modified(self, modified: bool):
        self._is_modified = modified
    
    def get_text(self) -> str:
        return self.toPlainText()
    
    def set_text(self, text: str):
        self.setPlainText(text)
        self._is_modified = False
    
    def load_file(self, file_path: str) -> bool:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.set_text(content)
            self._file_path = file_path
            self._is_modified = False
            return True
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法加载文件: {str(e)}")
            return False
    
    def save_file(self, file_path: Optional[str] = None) -> bool:
        path = file_path or self._file_path
        if not path:
            return False
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.get_text())
            self._file_path = path
            self._is_modified = False
            return True
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法保存文件: {str(e)}")
            return False


# ============== 编辑器标签页 ==============
class EditorTabWidget(QTabWidget):
    file_saved = pyqtSignal(str)
    file_modified = pyqtSignal(int, bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setDocumentMode(True)
        self.tabCloseRequested.connect(self._close_tab)
        self._editors: dict = {}
    
    def create_new_tab(self, title: str = "未命名.py", file_path: Optional[str] = None) -> CodeEditor:
        editor = CodeEditor()
        if file_path:
            editor.set_file_path(file_path)
        
        index = self.addTab(editor, title)
        self.setCurrentIndex(index)
        self._editors[index] = editor
        editor.modificationChanged.connect(lambda modified: self._on_editor_modified(index, modified))
        editor.syntax_error.connect(self._on_syntax_error)
        return editor
    
    def open_file(self, file_path: str) -> Optional[CodeEditor]:
        for i, editor in self._editors.items():
            if editor.get_file_path() == file_path:
                self.setCurrentIndex(i)
                return editor
        
        file_name = Path(file_path).name
        editor = CodeEditor()
        if editor.load_file(file_path):
            index = self.addTab(editor, file_name)
            self.setCurrentIndex(index)
            self._editors[index] = editor
            editor.modificationChanged.connect(lambda modified: self._on_editor_modified(index, modified))
            editor.syntax_error.connect(self._on_syntax_error)
            return editor
        return None
    
    def save_current_file(self) -> bool:
        editor = self.currentWidget()
        if isinstance(editor, CodeEditor):
            if editor.get_file_path():
                if editor.save_file():
                    self._update_tab_title(self.currentIndex(), editor)
                    self.file_saved.emit(editor.get_file_path())
                    return True
            else:
                return self.save_current_file_as()
        return False
    
    def save_current_file_as(self) -> bool:
        editor = self.currentWidget()
        if isinstance(editor, CodeEditor):
            file_path, _ = QFileDialog.getSaveFileName(
                self, "保存文件", "", "Python files (*.py);;All files (*.*)"
            )
            if file_path:
                if editor.save_file(file_path):
                    self._update_tab_title(self.currentIndex(), editor)
                    self.file_saved.emit(file_path)
                    return True
        return False
    
    def get_current_editor(self) -> Optional[CodeEditor]:
        widget = self.currentWidget()
        return widget if isinstance(widget, CodeEditor) else None
    
    def _close_tab(self, index: int):
        editor = self._editors.get(index)
        if editor and editor.is_modified():
            reply = QMessageBox.question(
                self, "未保存的更改",
                f"文件有未保存的更改，是否保存?",
                QMessageBox.StandardButton.Save | 
                QMessageBox.StandardButton.Discard | 
                QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Save:
                if not self.save_current_file():
                    return
            elif reply == QMessageBox.StandardButton.Cancel:
                return
        
        self.removeTab(index)
        if index in self._editors:
            del self._editors[index]
        
        new_editors = {}
        for i in range(self.count()):
            widget = self.widget(i)
            if isinstance(widget, CodeEditor):
                new_editors[i] = widget
        self._editors = new_editors
    
    def _on_editor_modified(self, index: int, modified: bool):
        title = self.tabText(index)
        if modified and not title.startswith("*"):
            self.setTabText(index, "*" + title)
        elif not modified and title.startswith("*"):
            self.setTabText(index, title[1:])
        self.file_modified.emit(index, modified)
    
    def _on_syntax_error(self, message: str):
        parent = self.parent()
        while parent and not isinstance(parent, QMainWindow):
            parent = parent.parent()
        if parent and hasattr(parent, '_statusbar'):
            if message:
                parent._statusbar.showMessage(message, 5000)
            else:
                parent._statusbar.showMessage("语法检查通过", 2000)
    
    def _update_tab_title(self, index: int, editor: CodeEditor):
        file_path = editor.get_file_path()
        if file_path:
            title = Path(file_path).name
            self.setTabText(index, title)
