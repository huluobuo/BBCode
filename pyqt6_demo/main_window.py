# -*- coding: utf-8 -*-
"""
BBCode PyQt6 主窗口示例
展示如何将 Tkinter UI 迁移到 PyQt6
"""

import sys
from typing import Optional

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QMenuBar, QMenu, QToolBar, QStatusBar, QSplitter, QTabWidget,
    QTextEdit, QTreeView, QDockWidget, QLabel,
    QPushButton, QLineEdit, QComboBox, QMessageBox, QProgressBar,
    QFrame, QStackedWidget, QScrollArea, QGridLayout
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QSize
from PyQt6.QtGui import QAction, QIcon, QFont, QPalette, QColor, QKeySequence, QShortcut, QFileSystemModel


class ModernStyle:
    """现代UI样式配置"""
    
    # 深色主题配色
    DARK_THEME = {
        'bg_primary': '#1e1e1e',
        'bg_secondary': '#252526',
        'bg_tertiary': '#2d2d30',
        'accent': '#007acc',
        'accent_hover': '#0098ff',
        'text_primary': '#cccccc',
        'text_secondary': '#858585',
        'border': '#3e3e42',
        'success': '#4ec9b0',
        'warning': '#ce9178',
        'error': '#f44747',
    }
    
    # 浅色主题配色
    LIGHT_THEME = {
        'bg_primary': '#ffffff',
        'bg_secondary': '#f3f3f3',
        'bg_tertiary': '#e8e8e8',
        'accent': '#0078d4',
        'accent_hover': '#106ebe',
        'text_primary': '#323130',
        'text_secondary': '#605e5c',
        'border': '#e0e0e0',
        'success': '#107c10',
        'warning': '#ffc107',
        'error': '#d13438',
    }
    
    @classmethod
    def apply_theme(cls, app: QApplication, dark: bool = True):
        """应用主题到应用程序"""
        theme = cls.DARK_THEME if dark else cls.LIGHT_THEME
        
        app.setStyle('Fusion')
        palette = QPalette()
        
        # 设置调色板
        palette.setColor(QPalette.ColorRole.Window, QColor(theme['bg_primary']))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(theme['text_primary']))
        palette.setColor(QPalette.ColorRole.Base, QColor(theme['bg_secondary']))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(theme['bg_tertiary']))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(theme['bg_primary']))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(theme['text_primary']))
        palette.setColor(QPalette.ColorRole.Text, QColor(theme['text_primary']))
        palette.setColor(QPalette.ColorRole.Button, QColor(theme['bg_tertiary']))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(theme['text_primary']))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(theme['accent']))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(theme['accent']))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor('#ffffff'))
        
        app.setPalette(palette)
        
        # 设置样式表
        app.setStyleSheet(cls.get_stylesheet(theme))
    
    @classmethod
    def get_stylesheet(cls, theme: dict) -> str:
        """获取样式表"""
        return f"""
        QMainWindow {{
            background-color: {theme['bg_primary']};
        }}
        
        QMenuBar {{
            background-color: {theme['bg_secondary']};
            color: {theme['text_primary']};
            border-bottom: 1px solid {theme['border']};
        }}
        
        QMenuBar::item:selected {{
            background-color: {theme['accent']};
            color: white;
        }}
        
        QMenu {{
            background-color: {theme['bg_secondary']};
            color: {theme['text_primary']};
            border: 1px solid {theme['border']};
        }}
        
        QMenu::item:selected {{
            background-color: {theme['accent']};
            color: white;
        }}
        
        QToolBar {{
            background-color: {theme['bg_secondary']};
            border-bottom: 1px solid {theme['border']};
            spacing: 5px;
            padding: 5px;
        }}
        
        QToolButton {{
            background-color: transparent;
            border: none;
            padding: 5px 10px;
            border-radius: 4px;
            color: {theme['text_primary']};
        }}
        
        QToolButton:hover {{
            background-color: {theme['bg_tertiary']};
        }}
        
        QToolButton:pressed {{
            background-color: {theme['accent']};
            color: white;
        }}
        
        QTabWidget::pane {{
            border: 1px solid {theme['border']};
            background-color: {theme['bg_primary']};
        }}
        
        QTabBar::tab {{
            background-color: {theme['bg_secondary']};
            color: {theme['text_secondary']};
            padding: 8px 16px;
            border: none;
            border-bottom: 2px solid transparent;
        }}
        
        QTabBar::tab:selected {{
            background-color: {theme['bg_primary']};
            color: {theme['text_primary']};
            border-bottom: 2px solid {theme['accent']};
        }}
        
        QTabBar::tab:hover:!selected {{
            background-color: {theme['bg_tertiary']};
            color: {theme['text_primary']};
        }}
        
        QTextEdit, QPlainTextEdit {{
            background-color: {theme['bg_secondary']};
            color: {theme['text_primary']};
            border: 1px solid {theme['border']};
            border-radius: 4px;
            padding: 5px;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 13px;
        }}
        
        QTreeView {{
            background-color: {theme['bg_secondary']};
            color: {theme['text_primary']};
            border: 1px solid {theme['border']};
            outline: none;
        }}
        
        QTreeView::item:selected {{
            background-color: {theme['accent']};
            color: white;
        }}
        
        QTreeView::item:hover {{
            background-color: {theme['bg_tertiary']};
        }}
        
        QPushButton {{
            background-color: {theme['accent']};
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }}
        
        QPushButton:hover {{
            background-color: {theme['accent_hover']};
        }}
        
        QPushButton:pressed {{
            background-color: {theme['accent']};
        }}
        
        QPushButton:disabled {{
            background-color: {theme['bg_tertiary']};
            color: {theme['text_secondary']};
        }}
        
        QLineEdit {{
            background-color: {theme['bg_secondary']};
            color: {theme['text_primary']};
            border: 1px solid {theme['border']};
            border-radius: 4px;
            padding: 6px;
        }}
        
        QLineEdit:focus {{
            border: 1px solid {theme['accent']};
        }}
        
        QComboBox {{
            background-color: {theme['bg_secondary']};
            color: {theme['text_primary']};
            border: 1px solid {theme['border']};
            border-radius: 4px;
            padding: 6px;
        }}
        
        QComboBox:hover {{
            border: 1px solid {theme['accent']};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {theme['bg_secondary']};
            color: {theme['text_primary']};
            border: 1px solid {theme['border']};
            selection-background-color: {theme['accent']};
        }}
        
        QStatusBar {{
            background-color: {theme['bg_secondary']};
            color: {theme['text_secondary']};
            border-top: 1px solid {theme['border']};
        }}
        
        QProgressBar {{
            border: none;
            background-color: {theme['bg_tertiary']};
            border-radius: 4px;
            height: 4px;
        }}
        
        QProgressBar::chunk {{
            background-color: {theme['accent']};
            border-radius: 4px;
        }}
        
        QSplitter::handle {{
            background-color: {theme['border']};
        }}
        
        QSplitter::handle:horizontal {{
            width: 2px;
        }}
        
        QSplitter::handle:vertical {{
            height: 2px;
        }}
        
        QDockWidget {{
            titlebar-close-icon: url(close.png);
            titlebar-normal-icon: url(undock.png);
        }}
        
        QDockWidget::title {{
            background-color: {theme['bg_secondary']};
            padding: 8px;
            border: 1px solid {theme['border']};
        }}
        
        QScrollBar:vertical {{
            background-color: {theme['bg_secondary']};
            width: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {theme['border']};
            border-radius: 6px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {theme['text_secondary']};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        
        QScrollBar:horizontal {{
            background-color: {theme['bg_secondary']};
            height: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: {theme['border']};
            border-radius: 6px;
            min-width: 20px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: {theme['text_secondary']};
        }}
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}
        """


class CodeEditor(QTextEdit):
    """代码编辑器组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptRichText(False)
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        
        # 设置等宽字体
        font = QFont("Consolas", 11)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        
        # 启用语法高亮（简化版）
        self._setup_syntax_highlighting()
    
    def _setup_syntax_highlighting(self):
        """设置基础语法高亮"""
        # 这里可以集成 QSyntaxHighlighter
        pass
    
    def get_text(self) -> str:
        """获取文本内容"""
        return self.toPlainText()
    
    def set_text(self, text: str):
        """设置文本内容"""
        self.setPlainText(text)


class FileExplorer(QTreeView):
    """文件浏览器组件"""
    
    file_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 设置文件系统模型
        self.model = QFileSystemModel()
        self.model.setRootPath('')
        self.setModel(self.model)
        
        # 隐藏不需要的列
        self.setColumnWidth(0, 200)
        self.setColumnHidden(1, True)  # 大小
        self.setColumnHidden(2, True)  # 类型
        self.setColumnHidden(3, True)  # 修改日期
        
        # 启用排序
        self.setSortingEnabled(True)
        
        # 连接信号
        self.clicked.connect(self._on_item_clicked)
        self.doubleClicked.connect(self._on_item_double_clicked)
    
    def set_root_path(self, path: str):
        """设置根路径"""
        self.setRootIndex(self.model.index(path))
    
    def _on_item_clicked(self, index):
        """项目点击处理"""
        path = self.model.filePath(index)
        self.file_selected.emit(path)
    
    def _on_item_double_clicked(self, index):
        """项目双击处理"""
        path = self.model.filePath(index)
        if self.model.isDir(index):
            self.setExpanded(index, not self.isExpanded(index))
        else:
            self.file_selected.emit(path)


class AIChatWidget(QWidget):
    """AI聊天组件"""
    
    message_sent = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 聊天显示区域
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setPlaceholderText("AI助手对话将显示在这里...")
        layout.addWidget(self.chat_display)
        
        # 输入区域
        input_layout = QHBoxLayout()
        
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("输入消息...")
        self.message_input.returnPressed.connect(self._send_message)
        input_layout.addWidget(self.message_input)
        
        self.send_button = QPushButton("发送")
        self.send_button.setFixedWidth(80)
        self.send_button.clicked.connect(self._send_message)
        input_layout.addWidget(self.send_button)
        
        layout.addLayout(input_layout)
        
        # 快捷按钮
        quick_layout = QHBoxLayout()
        
        quick_buttons = [
            ("解释代码", self._explain_code),
            ("优化代码", self._optimize_code),
            ("生成注释", self._generate_comments),
            ("修复错误", self._fix_errors),
        ]
        
        for text, callback in quick_buttons:
            btn = QPushButton(text)
            btn.setFixedHeight(28)
            btn.clicked.connect(callback)
            quick_layout.addWidget(btn)
        
        quick_layout.addStretch()
        layout.addLayout(quick_layout)
    
    def _send_message(self):
        """发送消息"""
        message = self.message_input.text().strip()
        if message:
            self._add_message("用户", message)
            self.message_sent.emit(message)
            self.message_input.clear()
    
    def _add_message(self, sender: str, message: str):
        """添加消息到显示区域"""
        color = "#4ecca3" if sender == "AI助手" else "#e94560"
        html = f'<p><b style="color: {color}">{sender}:</b> {message}</p>'
        self.chat_display.insertHtml(html)
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )
    
    def add_ai_response(self, response: str):
        """添加AI响应"""
        self._add_message("AI助手", response)
    
    def _explain_code(self):
        """解释代码"""
        self.message_input.setText("请解释这段代码")
    
    def _optimize_code(self):
        """优化代码"""
        self.message_input.setText("请优化这段代码")
    
    def _generate_comments(self):
        """生成注释"""
        self.message_input.setText("请为这段代码添加注释")
    
    def _fix_errors(self):
        """修复错误"""
        self.message_input.setText("请修复代码中的错误")


class TerminalWidget(QTextEdit):
    """终端/Shell组件"""
    
    command_entered = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(False)
        self.setPlaceholderText("Python Shell >>>")
        
        font = QFont("Consolas", 11)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        
        self._prompt = ">>> "
        self._history = []
        self._history_index = 0
        
        self._insert_prompt()
    
    def _insert_prompt(self):
        """插入提示符"""
        self.insertPlainText(self._prompt)
    
    def keyPressEvent(self, event):
        """键盘事件处理"""
        if event.key() == Qt.Key.Key_Return:
            # 获取当前行内容
            cursor = self.textCursor()
            cursor.movePosition(cursor.MoveOperation.StartOfLine)
            cursor.movePosition(cursor.MoveOperation.EndOfLine, cursor.MoveMode.KeepAnchor)
            line = cursor.selectedText()
            
            # 提取命令（去掉提示符）
            command = line[len(self._prompt):].strip()
            
            if command:
                self._history.append(command)
                self._history_index = len(self._history)
                self.command_entered.emit(command)
            
            self.insertPlainText("\n")
            self._insert_prompt()
        
        elif event.key() == Qt.Key.Key_Up:
            # 历史记录上翻
            if self._history_index > 0:
                self._history_index -= 1
                self._replace_current_line(self._history[self._history_index])
        
        elif event.key() == Qt.Key.Key_Down:
            # 历史记录下翻
            if self._history_index < len(self._history) - 1:
                self._history_index += 1
                self._replace_current_line(self._history[self._history_index])
            elif self._history_index == len(self._history) - 1:
                self._history_index += 1
                self._replace_current_line("")
        
        else:
            super().keyPressEvent(event)
    
    def _replace_current_line(self, text: str):
        """替换当前行"""
        cursor = self.textCursor()
        cursor.movePosition(cursor.MoveOperation.StartOfLine)
        cursor.movePosition(cursor.MoveOperation.EndOfLine, cursor.MoveMode.KeepAnchor)
        cursor.removeSelectedText()
        self._insert_prompt()
        self.insertPlainText(text)
    
    def append_output(self, output: str):
        """追加输出"""
        self.insertPlainText(output + "\n")
        self._insert_prompt()


class BBCodeMainWindow(QMainWindow):
    """BBCode PyQt6 主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BBCode - PyQt6 Edition")
        self.setGeometry(100, 100, 1400, 900)
        
        self._setup_ui()
        self._setup_menu()
        self._setup_toolbar()
        self._setup_statusbar()
    
    def _setup_ui(self):
        """设置主UI"""
        # 创建中央分割器
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(self.main_splitter)
        
        # 左侧文件浏览器
        self.file_explorer = FileExplorer()
        self.file_explorer.set_root_path(".")
        self.file_explorer.file_selected.connect(self._on_file_selected)
        
        file_dock = QDockWidget("文件浏览器", self)
        file_dock.setWidget(self.file_explorer)
        file_dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | 
            Qt.DockWidgetArea.RightDockWidgetArea
        )
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, file_dock)
        
        # 中央编辑器区域
        self.editor_tabs = QTabWidget()
        self.editor_tabs.setTabsClosable(True)
        self.editor_tabs.tabCloseRequested.connect(self._close_tab)
        self.main_splitter.addWidget(self.editor_tabs)
        
        # 右侧AI助手
        self.ai_chat = AIChatWidget()
        self.ai_chat.message_sent.connect(self._on_ai_message)
        
        ai_dock = QDockWidget("AI编程助手", self)
        ai_dock.setWidget(self.ai_chat)
        ai_dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | 
            Qt.DockWidgetArea.RightDockWidgetArea
        )
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, ai_dock)
        
        # 底部终端
        self.terminal = TerminalWidget()
        self.terminal.command_entered.connect(self._on_terminal_command)
        
        terminal_dock = QDockWidget("终端", self)
        terminal_dock.setWidget(self.terminal)
        terminal_dock.setAllowedAreas(
            Qt.DockWidgetArea.TopDockWidgetArea | 
            Qt.DockWidgetArea.BottomDockWidgetArea
        )
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, terminal_dock)
        
        # 设置分割器比例
        self.main_splitter.setSizes([250, 900, 250])
    
    def _setup_menu(self):
        """设置菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")
        
        new_file_action = QAction("新建文件", self)
        new_file_action.setShortcut(QKeySequence.StandardKey.New)
        new_file_action.triggered.connect(self._new_file)
        file_menu.addAction(new_file_action)
        
        open_file_action = QAction("打开文件", self)
        open_file_action.setShortcut(QKeySequence.StandardKey.Open)
        open_file_action.triggered.connect(self._open_file)
        file_menu.addAction(open_file_action)
        
        open_folder_action = QAction("打开文件夹", self)
        open_folder_action.triggered.connect(self._open_folder)
        file_menu.addAction(open_folder_action)
        
        file_menu.addSeparator()
        
        save_action = QAction("保存", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self._save_file)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("退出", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 编辑菜单
        edit_menu = menubar.addMenu("编辑(&E)")
        
        undo_action = QAction("撤销", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(self._undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("重做", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(self._redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        cut_action = QAction("剪切", self)
        cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        cut_action.triggered.connect(self._cut)
        edit_menu.addAction(cut_action)
        
        copy_action = QAction("复制", self)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.triggered.connect(self._copy)
        edit_menu.addAction(copy_action)
        
        paste_action = QAction("粘贴", self)
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.triggered.connect(self._paste)
        edit_menu.addAction(paste_action)
        
        # 运行菜单
        run_menu = menubar.addMenu("运行(&R)")
        
        run_action = QAction("运行", self)
        run_action.setShortcut("F5")
        run_action.triggered.connect(self._run_code)
        run_menu.addAction(run_action)
        
        debug_action = QAction("调试", self)
        debug_action.setShortcut("F9")
        debug_action.triggered.connect(self._debug_code)
        run_menu.addAction(debug_action)
        
        # 视图菜单
        view_menu = menubar.addMenu("视图(&V)")
        
        toggle_theme_action = QAction("切换主题", self)
        toggle_theme_action.triggered.connect(self._toggle_theme)
        view_menu.addAction(toggle_theme_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")
        
        about_action = QAction("关于", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _setup_toolbar(self):
        """设置工具栏"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # 新建文件
        new_btn = QPushButton("新建")
        new_btn.setFixedHeight(32)
        new_btn.clicked.connect(self._new_file)
        toolbar.addWidget(new_btn)
        
        # 打开文件
        open_btn = QPushButton("打开")
        open_btn.setFixedHeight(32)
        open_btn.clicked.connect(self._open_file)
        toolbar.addWidget(open_btn)
        
        # 保存
        save_btn = QPushButton("保存")
        save_btn.setFixedHeight(32)
        save_btn.clicked.connect(self._save_file)
        toolbar.addWidget(save_btn)
        
        toolbar.addSeparator()
        
        # 运行
        run_btn = QPushButton("▶ 运行")
        run_btn.setFixedHeight(32)
        run_btn.setStyleSheet("background-color: #4ec9b0;")
        run_btn.clicked.connect(self._run_code)
        toolbar.addWidget(run_btn)
        
        # 调试
        debug_btn = QPushButton("🐛 调试")
        debug_btn.setFixedHeight(32)
        debug_btn.clicked.connect(self._debug_code)
        toolbar.addWidget(debug_btn)
        
        toolbar.addSeparator()
        
        # 后端选择
        backend_label = QLabel("后端:")
        toolbar.addWidget(backend_label)
        
        self.backend_combo = QComboBox()
        self.backend_combo.addItems([
            "Local Python 3.11",
            "MicroPython (ESP32)",
            "CircuitPython",
            "Remote Python"
        ])
        self.backend_combo.setFixedWidth(180)
        self.backend_combo.setFixedHeight(28)
        toolbar.addWidget(self.backend_combo)
    
    def _setup_statusbar(self):
        """设置状态栏"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        self.statusbar.showMessage("就绪")
        
        # 添加进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(150)
        self.progress_bar.setVisible(False)
        self.statusbar.addPermanentWidget(self.progress_bar)
    
    def _new_file(self):
        """新建文件"""
        editor = CodeEditor()
        index = self.editor_tabs.addTab(editor, "未命名.py")
        self.editor_tabs.setCurrentIndex(index)
    
    def _open_file(self):
        """打开文件"""
        from PyQt6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开文件", "", "Python files (*.py);;All files (*.*)"
        )
        if file_path:
            self._load_file(file_path)
    
    def _open_folder(self):
        """打开文件夹"""
        from PyQt6.QtWidgets import QFileDialog
        folder_path = QFileDialog.getExistingDirectory(self, "打开文件夹")
        if folder_path:
            self.file_explorer.set_root_path(folder_path)
    
    def _load_file(self, file_path: str):
        """加载文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            editor = CodeEditor()
            editor.set_text(content)
            
            import os
            file_name = os.path.basename(file_path)
            index = self.editor_tabs.addTab(editor, file_name)
            self.editor_tabs.setCurrentIndex(index)
            
            self.statusbar.showMessage(f"已打开: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法打开文件: {str(e)}")
    
    def _save_file(self):
        """保存文件"""
        current_widget = self.editor_tabs.currentWidget()
        if isinstance(current_widget, CodeEditor):
            from PyQt6.QtWidgets import QFileDialog
            file_path, _ = QFileDialog.getSaveFileName(
                self, "保存文件", "", "Python files (*.py);;All files (*.*)"
            )
            if file_path:
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(current_widget.get_text())
                    self.statusbar.showMessage(f"已保存: {file_path}")
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"无法保存文件: {str(e)}")
    
    def _close_tab(self, index: int):
        """关闭标签页"""
        self.editor_tabs.removeTab(index)
    
    def _on_file_selected(self, file_path: str):
        """文件选择处理"""
        import os
        if os.path.isfile(file_path) and file_path.endswith('.py'):
            self._load_file(file_path)
    
    def _on_ai_message(self, message: str):
        """AI消息处理"""
        # 模拟AI响应
        self.ai_chat.add_ai_response(f"收到您的消息: {message}\n这是一个模拟响应。")
    
    def _on_terminal_command(self, command: str):
        """终端命令处理"""
        # 模拟执行命令
        self.terminal.append_output(f"执行: {command}")
        self.terminal.append_output("命令执行完成。")
    
    def _run_code(self):
        """运行代码"""
        current_widget = self.editor_tabs.currentWidget()
        if isinstance(current_widget, CodeEditor):
            code = current_widget.get_text()
            self.terminal.append_output("运行代码...")
            self.terminal.append_output("代码执行完成！")
    
    def _debug_code(self):
        """调试代码"""
        self.statusbar.showMessage("调试模式已启动")
    
    def _toggle_theme(self):
        """切换主题"""
        # 这里可以实现主题切换逻辑
        QMessageBox.information(self, "主题", "主题切换功能")
    
    def _undo(self):
        """撤销"""
        current_widget = self.editor_tabs.currentWidget()
        if isinstance(current_widget, CodeEditor):
            current_widget.undo()
    
    def _redo(self):
        """重做"""
        current_widget = self.editor_tabs.currentWidget()
        if isinstance(current_widget, CodeEditor):
            current_widget.redo()
    
    def _cut(self):
        """剪切"""
        current_widget = self.editor_tabs.currentWidget()
        if isinstance(current_widget, CodeEditor):
            current_widget.cut()
    
    def _copy(self):
        """复制"""
        current_widget = self.editor_tabs.currentWidget()
        if isinstance(current_widget, CodeEditor):
            current_widget.copy()
    
    def _paste(self):
        """粘贴"""
        current_widget = self.editor_tabs.currentWidget()
        if isinstance(current_widget, CodeEditor):
            current_widget.paste()
    
    def _show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于 BBCode",
            "<h2>BBCode PyQt6 Edition</h2>"
            "<p>基于 PyQt6 的现代化 Python IDE</p>"
            "<p>版本: 1.0.0</p>"
        )


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 应用现代主题
    ModernStyle.apply_theme(app, dark=True)
    
    # 创建主窗口
    window = BBCodeMainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
