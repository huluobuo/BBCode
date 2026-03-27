# -*- coding: utf-8 -*-
"""
BBCode 代码编辑器组件
支持行号显示、语法高亮、语法检查
"""

import re
from typing import Optional, List, Tuple
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit, QTextEdit,
    QLabel, QFrame, QScrollArea, QApplication
)
from PyQt6.QtCore import Qt, QRect, pyqtSignal, QTimer
from PyQt6.QtGui import (
    QFont, QColor, QPainter, QTextFormat, QTextCharFormat,
    QSyntaxHighlighter, QTextCursor, QTextDocument, QKeyEvent
)


class PythonSyntaxHighlighter(QSyntaxHighlighter):
    """Python 语法高亮器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 定义颜色
        self.colors = {
            'keyword': QColor("#569cd6"),      # 蓝色 - 关键字
            'string': QColor("#ce9178"),       # 橙色 - 字符串
            'comment': QColor("#6a9955"),      # 绿色 - 注释
            'function': QColor("#dcdcaa"),     # 黄色 - 函数
            'number': QColor("#b5cea8"),       # 浅绿 - 数字
            'operator': QColor("#d4d4d4"),     # 白色 - 运算符
            'builtin': QColor("#4ec9b0"),      # 青色 - 内置函数
            'class': QColor("#4ec9b0"),        # 青色 - 类名
        }
        
        # 关键字
        self.keywords = [
            'and', 'as', 'assert', 'break', 'class', 'continue', 'def',
            'del', 'elif', 'else', 'except', 'False', 'finally', 'for',
            'from', 'global', 'if', 'import', 'in', 'is', 'lambda',
            'None', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return',
            'True', 'try', 'while', 'with', 'yield', 'async', 'await'
        ]
        
        # 内置函数
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
        
        # 编译正则表达式
        self.rules = []
        
        # 关键字
        self.rules.append((
            r'\b(' + '|'.join(self.keywords) + r')\b',
            self.colors['keyword']
        ))
        
        # 内置函数
        self.rules.append((
            r'\b(' + '|'.join(self.builtins) + r')(?=\s*\()',
            self.colors['builtin']
        ))
        
        # 类名（大写字母开头）
        self.rules.append((
            r'\b[A-Z][a-zA-Z0-9_]*\b',
            self.colors['class']
        ))
        
        # 函数定义
        self.rules.append((
            r'\bdef\s+(\w+)',
            self.colors['function']
        ))
        
        # 类定义
        self.rules.append((
            r'\bclass\s+(\w+)',
            self.colors['class']
        ))
        
        # 字符串（单引号）
        self.rules.append((
            r"'[^'\\]*(\\.[^'\\]*)*'",
            self.colors['string']
        ))
        
        # 字符串（双引号）
        self.rules.append((
            r'"[^"\\]*(\\.[^"\\]*)*"',
            self.colors['string']
        ))
        
        # 三引号字符串
        self.rules.append((
            r"'''[^']*'''",
            self.colors['string']
        ))
        self.rules.append((
            r'"""[^"]*"""',
            self.colors['string']
        ))
        
        # 数字
        self.rules.append((
            r'\b\d+\.?\d*\b',
            self.colors['number']
        ))
        
        # 注释
        self.rules.append((
            r'#[^\n]*',
            self.colors['comment']
        ))
        
        # 运算符
        self.rules.append((
            r'[\+\-\*\/\%\=\<\>\!\&\|\^\~]',
            self.colors['operator']
        ))
    
    def highlightBlock(self, text):
        """高亮文本块"""
        for pattern, color in self.rules:
            expression = re.compile(pattern)
            for match in expression.finditer(text):
                start = match.start()
                end = match.end()
                
                # 检查是否在注释或字符串内
                if self._is_in_comment_or_string(text, start):
                    continue
                
                format = QTextCharFormat()
                format.setForeground(color)
                self.setFormat(start, end - start, format)
    
    def _is_in_comment_or_string(self, text, pos):
        """检查位置是否在注释或字符串内"""
        # 简单检查：如果在 # 之后，则是注释
        comment_pos = text.find('#')
        if comment_pos != -1 and pos > comment_pos:
            return True
        return False


class LineNumberArea(QWidget):
    """行号区域"""
    
    def __init__(self, editor):
        super().__init__(editor)
        self._editor = editor
    
    def sizeHint(self):
        return self._editor.line_number_area_width()
    
    def paintEvent(self, event):
        self._editor.line_number_area_paint_event(event)


class CodeEditor(QPlainTextEdit):
    """代码编辑器 - 支持行号、语法高亮、语法检查"""
    
    text_changed = pyqtSignal()
    cursor_position_changed = pyqtSignal(int, int)
    syntax_error = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._file_path: Optional[str] = None
        self._is_modified = False
        self._syntax_error_line: Optional[int] = None  # 语法错误行号
        
        # 基础设置
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        
        # 设置等宽字体
        font = QFont("Consolas", 12)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        
        # 设置 Tab 宽度
        self.setTabStopDistance(40)
        
        # 创建行号区域
        self._line_number_area = LineNumberArea(self)
        
        # 连接信号
        self.blockCountChanged.connect(self._update_line_number_area_width)
        self.updateRequest.connect(self._update_line_number_area)
        self.cursorPositionChanged.connect(self._highlight_current_line)
        self.textChanged.connect(self._on_text_changed)
        
        # 初始化行号区域宽度
        self._update_line_number_area_width(0)
        
        # 设置语法高亮
        self._highlighter = PythonSyntaxHighlighter(self.document())
        
        # 语法检查定时器
        self._syntax_check_timer = QTimer(self)
        self._syntax_check_timer.timeout.connect(self._check_syntax)
        self._syntax_check_timer.setSingleShot(True)
        
        # 当前行高亮
        self._highlight_current_line()
    
    def line_number_area_width(self):
        """计算行号区域宽度"""
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1
        
        space = 10 + self.fontMetrics().horizontalAdvance('9') * digits
        return space
    
    def _update_line_number_area_width(self, _):
        """更新行号区域宽度"""
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)
    
    def _update_line_number_area(self, rect, dy):
        """更新行号区域"""
        if dy:
            self._line_number_area.scroll(0, dy)
        else:
            self._line_number_area.update(0, rect.y(), self._line_number_area.width(), rect.height())
        
        if rect.contains(self.viewport().rect()):
            self._update_line_number_area_width(0)
    
    def resizeEvent(self, event):
        """调整大小事件"""
        super().resizeEvent(event)
        
        cr = self.contentsRect()
        self._line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )
    
    def line_number_area_paint_event(self, event):
        """绘制行号"""
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
        """高亮当前行和语法错误"""
        extra_selections = []
        
        # 当前行高亮
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor("#2d2d30")
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        
        # 语法错误下划线
        if hasattr(self, '_syntax_error_line') and self._syntax_error_line is not None:
            error_selection = QTextEdit.ExtraSelection()
            error_color = QColor("#ff6b6b")
            error_selection.format.setUnderlineColor(error_color)
            error_selection.format.setUnderlineStyle(QTextCharFormat.UnderlineStyle.SpellCheckUnderline)
            error_selection.format.setBackground(QColor("#3d1f1f"))
            
            # 选择错误行
            cursor = QTextCursor(self.document())
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            for _ in range(self._syntax_error_line - 1):
                cursor.movePosition(QTextCursor.MoveOperation.NextBlock)
            cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
            
            error_selection.cursor = cursor
            extra_selections.append(error_selection)
        
        self.setExtraSelections(extra_selections)
        
        # 更新光标位置信号
        cursor = self.textCursor()
        self.cursor_position_changed.emit(cursor.blockNumber() + 1, cursor.columnNumber() + 1)
    
    def _on_text_changed(self):
        """文本变更处理"""
        if not self._is_modified:
            self._is_modified = True
            self.text_changed.emit()
        
        # 延迟语法检查
        self._syntax_check_timer.stop()
        self._syntax_check_timer.start(1000)  # 1秒后检查
    
    def _check_syntax(self):
        """检查语法错误"""
        code = self.toPlainText()
        if not code.strip():
            self._syntax_error_line = None
            self._highlight_current_line()
            self.syntax_error.emit("")
            return
        
        try:
            compile(code, '<string>', 'exec')
            # 语法正确
            self._syntax_error_line = None
            self._highlight_current_line()
            self.syntax_error.emit("")
        except SyntaxError as e:
            error_msg = f"语法错误 (行 {e.lineno}): {e.msg}"
            self._syntax_error_line = e.lineno
            self._highlight_current_line()
            self.syntax_error.emit(error_msg)
        except Exception as e:
            error_msg = f"错误: {str(e)}"
            self._syntax_error_line = None
            self._highlight_current_line()
            self.syntax_error.emit(error_msg)
    
    def get_file_path(self) -> Optional[str]:
        """获取文件路径"""
        return self._file_path
    
    def set_file_path(self, path: str):
        """设置文件路径"""
        self._file_path = path
    
    def is_modified(self) -> bool:
        """检查是否已修改"""
        return self._is_modified
    
    def set_modified(self, modified: bool):
        """设置修改状态"""
        self._is_modified = modified
    
    def get_text(self) -> str:
        """获取文本内容"""
        return self.toPlainText()
    
    def set_text(self, text: str):
        """设置文本内容"""
        self.setPlainText(text)
        self._is_modified = False
    
    def load_file(self, file_path: str) -> bool:
        """加载文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.set_text(content)
            self._file_path = file_path
            self._is_modified = False
            return True
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "错误", f"无法加载文件: {str(e)}")
            return False
    
    def save_file(self, file_path: Optional[str] = None) -> bool:
        """保存文件"""
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
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "错误", f"无法保存文件: {str(e)}")
            return False


# 为了兼容性，保留原来的名称
class EditorTabWidget:
    """兼容原来的 EditorTabWidget"""
    pass
