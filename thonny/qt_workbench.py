# -*- coding: utf-8 -*-
"""
BBCode PyQt6 Workbench - 核心UI模块
基于 PyQt6 的现代化 IDE 主窗口
"""

import sys
import os
from pathlib import Path
from typing import Optional, Dict, List, Callable, Any

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QMenuBar, QMenu, QToolBar, QStatusBar, QSplitter, QTabWidget,
    QTextEdit, QTreeView, QDockWidget, QLabel,
    QPushButton, QLineEdit, QComboBox, QMessageBox, QProgressBar,
    QFrame, QStackedWidget, QFileDialog, QInputDialog,
    QToolButton, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QSize, QSettings
from PyQt6.QtGui import QAction, QIcon, QFont, QKeySequence, QCloseEvent, QFileSystemModel

from thonny.qt_themes import ThemeManager, apply_theme, get_theme_manager
from thonny.code_editor import CodeEditor


class FileExplorer(QWidget):
    """文件浏览器组件 - 带工具栏"""
    
    file_selected = pyqtSignal(str)
    file_double_clicked = pyqtSignal(str)
    root_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._current_root = str(Path.home())
        self._setup_ui()
        self.set_root_path(self._current_root)
    
    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 工具栏
        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(8, 4, 8, 4)
        toolbar.setSpacing(4)
        
        # 上一级按钮
        self._up_btn = QPushButton("⬆ 上一级")
        self._up_btn.setFixedHeight(28)
        self._up_btn.clicked.connect(self._go_to_parent)
        toolbar.addWidget(self._up_btn)
        
        # 当前路径标签
        self._path_label = QLabel()
        self._path_label.setStyleSheet("color: #888; font-size: 11px;")
        self._path_label.setWordWrap(True)
        toolbar.addWidget(self._path_label, 1)
        
        # 刷新按钮
        refresh_btn = QPushButton("🔄")
        refresh_btn.setFixedSize(28, 28)
        refresh_btn.setToolTip("刷新")
        refresh_btn.clicked.connect(self._refresh)
        toolbar.addWidget(refresh_btn)
        
        layout.addLayout(toolbar)
        
        # 文件树
        self._tree = QTreeView()
        self._model = QFileSystemModel()
        self._model.setRootPath('')
        self._tree.setModel(self._model)
        
        # 配置显示
        self._tree.setColumnWidth(0, 250)
        self._tree.setColumnHidden(1, True)  # 大小
        self._tree.setColumnHidden(2, True)  # 类型
        self._tree.setColumnHidden(3, True)  # 修改日期
        
        # 启用排序
        self._tree.setSortingEnabled(True)
        
        # 设置选择模式
        self._tree.setSelectionMode(QTreeView.SelectionMode.SingleSelection)
        
        # 连接信号
        self._tree.clicked.connect(self._on_item_clicked)
        self._tree.doubleClicked.connect(self._on_item_double_clicked)
        
        layout.addWidget(self._tree)
    
    def _go_to_parent(self):
        """转到父文件夹"""
        parent = Path(self._current_root).parent
        if parent.exists():
            self.set_root_path(str(parent))
    
    def _refresh(self):
        """刷新"""
        self._model.setRootPath('')
        self.set_root_path(self._current_root)
    
    def _update_path_label(self):
        """更新路径标签"""
        # 显示短路径
        path = Path(self._current_root)
        try:
            # 尝试显示相对于home的路径
            short_path = path.relative_to(Path.home())
            display = f"~/{short_path}"
        except ValueError:
            display = str(path)
        
        # 如果太长，显示最后两部分
        if len(display) > 40:
            parts = display.split('/')
            if len(parts) > 2:
                display = ".../" + "/".join(parts[-2:])
        
        self._path_label.setText(display)
        self._path_label.setToolTip(self._current_root)
    
    def set_root_path(self, path: str):
        """设置根路径"""
        self._current_root = path
        self._tree.setRootIndex(self._model.index(path))
        self._update_path_label()
        self.root_changed.emit(path)
        
        # 更新上一级按钮状态
        parent = Path(path).parent
        self._up_btn.setEnabled(parent.exists() and parent != Path(path))
    
    def get_current_root(self) -> str:
        """获取当前根路径"""
        return self._current_root
    
    def get_selected_path(self) -> Optional[str]:
        """获取选中的路径"""
        indexes = self._tree.selectedIndexes()
        if indexes:
            return self._model.filePath(indexes[0])
        return None
    
    def _on_item_clicked(self, index):
        """项目点击处理"""
        path = self._model.filePath(index)
        self.file_selected.emit(path)
    
    def _on_item_double_clicked(self, index):
        """项目双击处理"""
        path = self._model.filePath(index)
        if self._model.isDir(index):
            # 双击文件夹时进入该文件夹
            self.set_root_path(path)
        else:
            self.file_double_clicked.emit(path)


class EditorTabWidget(QTabWidget):
    """编辑器标签页组件 - 带自定义关闭按钮"""

    file_saved = pyqtSignal(str)
    file_modified = pyqtSignal(int, bool)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTabsClosable(True)
        self.setMovable(True)
        self.setDocumentMode(True)

        # 设置标签样式
        self.setStyleSheet("""
            QTabBar::tab {
                padding: 8px 24px 8px 12px;
            }
            QTabBar::close-button {
                image: none;
                width: 14px;
                height: 14px;
            }
        """)

        # 连接信号
        self.tabCloseRequested.connect(self._close_tab)

        # 存储编辑器映射
        self._editors: Dict[int, CodeEditor] = {}
    
    def create_new_tab(self, title: str = "未命名.py", file_path: Optional[str] = None) -> CodeEditor:
        """创建新标签页"""
        editor = CodeEditor()
        editor.set_file_path(file_path) if file_path else None

        index = self.addTab(editor, title)
        self.setCurrentIndex(index)

        self._editors[index] = editor
        editor.modificationChanged.connect(lambda modified: self._on_editor_modified(index, modified))
        editor.syntax_error.connect(self._on_syntax_error)
        editor.cursorPositionChanged.connect(self._on_cursor_position_changed)

        return editor

    def open_file(self, file_path: str) -> Optional[CodeEditor]:
        """打开文件"""
        # 检查是否已打开
        for i, editor in self._editors.items():
            if editor.get_file_path() == file_path:
                self.setCurrentIndex(i)
                return editor

        # 创建新标签页
        file_name = os.path.basename(file_path)
        editor = CodeEditor()

        if editor.load_file(file_path):
            index = self.addTab(editor, file_name)
            self.setCurrentIndex(index)
            self._editors[index] = editor
            editor.modificationChanged.connect(lambda modified: self._on_editor_modified(index, modified))
            editor.syntax_error.connect(self._on_syntax_error)
            editor.cursorPositionChanged.connect(self._on_cursor_position_changed)
            return editor

        return None
    
    def save_current_file(self) -> bool:
        """保存当前文件"""
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
        """另存为当前文件"""
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
        """获取当前编辑器"""
        widget = self.currentWidget()
        return widget if isinstance(widget, CodeEditor) else None
    
    def _close_tab(self, index: int):
        """关闭标签页"""
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
        
        # 重新映射索引
        new_editors = {}
        for i in range(self.count()):
            widget = self.widget(i)
            if isinstance(widget, CodeEditor):
                new_editors[i] = widget
        self._editors = new_editors
    
    def _on_editor_modified(self, index: int, modified: bool):
        """编辑器修改处理"""
        editor = self._editors.get(index)
        if editor:
            title = self.tabText(index)
            if modified and not title.startswith("*"):
                self.setTabText(index, "*" + title)
            elif not modified and title.startswith("*"):
                self.setTabText(index, title[1:])
            self.file_modified.emit(index, modified)

    def _on_syntax_error(self, message: str):
        """语法错误处理"""
        # 获取主窗口并更新状态栏
        parent = self.parent()
        while parent and not isinstance(parent, QtWorkbench):
            parent = parent.parent()
        if parent and isinstance(parent, QtWorkbench):
            if message:
                parent._statusbar.showMessage(f"语法错误: {message}", 5000)
            else:
                parent._statusbar.showMessage("语法检查通过", 2000)

    def _on_cursor_position_changed(self):
        """光标位置变化处理"""
        editor = self.currentWidget()
        if isinstance(editor, CodeEditor):
            cursor = editor.textCursor()
            line = cursor.blockNumber() + 1
            col = cursor.columnNumber() + 1

            # 获取主窗口并更新状态栏
            parent = self.parent()
            while parent and not isinstance(parent, QtWorkbench):
                parent = parent.parent()
            if parent and isinstance(parent, QtWorkbench):
                parent._position_label.setText(f"行 {line}, 列 {col}")
    
    def _update_tab_title(self, index: int, editor: CodeEditor):
        """更新标签页标题"""
        file_path = editor.get_file_path()
        if file_path:
            title = os.path.basename(file_path)
            self.setTabText(index, title)


class QtWorkbench(QMainWindow):
    """PyQt6 版本的 BBCode Workbench"""
    
    # 信号
    editor_created = pyqtSignal(object)
    file_opened = pyqtSignal(str)
    file_saved = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("BBCode - PyQt6 Edition")
        self.setGeometry(100, 100, 1600, 1000)
        
        # 初始化设置
        self._settings = QSettings("BBCode", "PyQt6Edition")
        
        # 初始化UI（停靠窗口由外部设置）
        self._setup_menu()
        self._setup_toolbar()
        self._setup_statusbar()
        self._setup_dock_widgets()
        
        # 注意：_setup_ui 和初始编辑器由外部调用
    
    def _setup_ui(self):
        """设置主UI"""
        # 创建中央分割器
        self._central_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(self._central_splitter)
        
        # 编辑器标签页
        self._editor_tabs = EditorTabWidget()
        self._editor_tabs.file_saved.connect(self._on_file_saved)
        self._central_splitter.addWidget(self._editor_tabs)
        
        # 设置分割器比例
        self._central_splitter.setSizes([1200, 400])
    
    def _setup_menu(self):
        """设置菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")
        
        new_action = QAction("新建文件", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self._new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction("打开文件...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._open_file)
        file_menu.addAction(open_action)
        
        open_folder_action = QAction("打开文件夹...", self)
        open_folder_action.triggered.connect(self._open_folder)
        file_menu.addAction(open_folder_action)
        
        file_menu.addSeparator()
        
        save_action = QAction("保存", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self._save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("另存为...", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self._save_file_as)
        file_menu.addAction(save_as_action)
        
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
        
        # 主题子菜单
        theme_menu = view_menu.addMenu("主题")
        
        for theme_name in get_theme_manager().get_available_themes():
            action = QAction(theme_name, self)
            action.triggered.connect(lambda checked, t=theme_name: self._change_theme(t))
            theme_menu.addAction(action)
        
        view_menu.addSeparator()

        # 面板显示选项
        self._show_file_explorer_action = QAction("📁 文件浏览器", self)
        self._show_file_explorer_action.setCheckable(True)
        self._show_file_explorer_action.setChecked(True)
        view_menu.addAction(self._show_file_explorer_action)

        self._show_ai_chat_action = QAction("🤖 AI 编程助手", self)
        self._show_ai_chat_action.setCheckable(True)
        self._show_ai_chat_action.setChecked(True)
        view_menu.addAction(self._show_ai_chat_action)

        self._show_terminal_action = QAction("⌨ Shell", self)
        self._show_terminal_action.setCheckable(True)
        self._show_terminal_action.setChecked(True)
        view_menu.addAction(self._show_terminal_action)

        view_menu.addSeparator()

        # 重置布局
        reset_layout_action = QAction("重置布局", self)
        reset_layout_action.triggered.connect(self._reset_layout)
        view_menu.addAction(reset_layout_action)

        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")
        
        about_action = QAction("关于", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _setup_toolbar(self):
        """设置工具栏"""
        toolbar = QToolBar("主工具栏")
        self.addToolBar(toolbar)
        
        # 文件操作
        new_btn = QToolButton()
        new_btn.setText("新建")
        new_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        new_btn.clicked.connect(self._new_file)
        toolbar.addWidget(new_btn)
        
        open_btn = QToolButton()
        open_btn.setText("打开")
        open_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        open_btn.clicked.connect(self._open_file)
        toolbar.addWidget(open_btn)
        
        save_btn = QToolButton()
        save_btn.setText("保存")
        save_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        save_btn.clicked.connect(self._save_file)
        toolbar.addWidget(save_btn)
        
        toolbar.addSeparator()
        
        # 运行操作
        run_btn = QPushButton("▶ 运行")
        run_btn.setObjectName("success")
        run_btn.setFixedHeight(32)
        run_btn.clicked.connect(self._run_code)
        toolbar.addWidget(run_btn)
        
        debug_btn = QPushButton("🐛 调试")
        debug_btn.setFixedHeight(32)
        debug_btn.clicked.connect(self._debug_code)
        toolbar.addWidget(debug_btn)
        
        toolbar.addSeparator()
        
        # 后端选择
        toolbar.addWidget(QLabel("后端: "))
        
        self._backend_combo = QComboBox()
        self._backend_combo.addItems([
            "Local Python 3.11",
            "MicroPython (ESP32)",
            "CircuitPython",
            "Remote Python"
        ])
        self._backend_combo.setFixedWidth(180)
        toolbar.addWidget(self._backend_combo)
    
    def _setup_statusbar(self):
        """设置状态栏"""
        self._statusbar = QStatusBar()
        self.setStatusBar(self._statusbar)
        
        self._statusbar.showMessage("就绪")
        
        # 添加进度条
        self._progress_bar = QProgressBar()
        self._progress_bar.setMaximumWidth(150)
        self._progress_bar.setVisible(False)
        self._statusbar.addPermanentWidget(self._progress_bar)
        
        # 添加行列指示器
        self._position_label = QLabel("行 1, 列 1")
        self._statusbar.addPermanentWidget(self._position_label)
    
    def _setup_dock_widgets(self):
        """设置停靠窗口 - 文件浏览器由外部创建"""
        # 文件浏览器将在外部创建并添加
        self._file_explorer = None
        self._file_dock = None
    
    def set_file_explorer(self, file_explorer: FileExplorer, dock: QDockWidget):
        """设置文件浏览器"""
        self._file_explorer = file_explorer
        self._file_dock = dock
        self._file_explorer.file_double_clicked.connect(self._on_file_explorer_double_click)
        self._show_file_explorer_action.triggered.connect(dock.setVisible)
        # 同步动作和窗口状态
        dock.visibilityChanged.connect(self._show_file_explorer_action.setChecked)

    def set_ai_chat(self, ai_chat, dock: QDockWidget):
        """设置 AI 聊天"""
        self._ai_chat = ai_chat
        self._ai_dock = dock
        self._show_ai_chat_action.triggered.connect(dock.setVisible)
        # 同步动作和窗口状态
        dock.visibilityChanged.connect(self._show_ai_chat_action.setChecked)

    def set_terminal(self, terminal, dock: QDockWidget):
        """设置终端"""
        self._terminal = terminal
        self._terminal_dock = dock
        self._show_terminal_action.triggered.connect(dock.setVisible)
        # 同步动作和窗口状态
        dock.visibilityChanged.connect(self._show_terminal_action.setChecked)

    def _reset_layout(self):
        """重置布局"""
        # 恢复默认布局
        if hasattr(self, '_file_dock') and self._file_dock:
            self._file_dock.setVisible(True)
            self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self._file_dock)

        if hasattr(self, '_ai_dock') and self._ai_dock:
            self._ai_dock.setVisible(True)
            self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self._ai_dock)

        if hasattr(self, '_terminal_dock') and self._terminal_dock:
            self._terminal_dock.setVisible(True)
            self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self._terminal_dock)

        # 重置分割器大小
        self._central_splitter.setSizes([250, 900, 350])

        self._statusbar.showMessage("布局已重置", 3000)
    
    def _load_settings(self):
        """加载设置"""
        # 恢复窗口几何
        geometry = self._settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
        # 恢复窗口状态
        state = self._settings.value("windowState")
        if state:
            self.restoreState(state)
        
        # 恢复上次打开的文件夹
        last_folder = self._settings.value("lastFolder")
        if last_folder and Path(last_folder).exists():
            self._file_explorer.set_root_path(last_folder)
        
        # 恢复打开的文件
        open_files = self._settings.value("openFiles")
        if open_files:
            files = open_files.split(";")
            for file_path in files:
                if Path(file_path).exists():
                    self._editor_tabs.open_file(file_path)
        
        # 恢复文件浏览器根路径
        explorer_root = self._settings.value("explorerRoot")
        if explorer_root and Path(explorer_root).exists():
            self._file_explorer.set_root_path(explorer_root)
    
    def _save_settings(self):
        """保存设置"""
        self._settings.setValue("geometry", self.saveGeometry())
        self._settings.setValue("windowState", self.saveState())
        
        # 保存当前文件夹
        current_root = self._file_explorer.get_current_root()
        self._settings.setValue("lastFolder", current_root)
        self._settings.setValue("explorerRoot", current_root)
        
        # 保存打开的文件列表
        open_files = []
        for i in range(self._editor_tabs.count()):
            editor = self._editor_tabs.widget(i)
            if isinstance(editor, CodeEditor):
                file_path = editor.get_file_path()
                if file_path:
                    open_files.append(file_path)
        
        if open_files:
            self._settings.setValue("openFiles", ";".join(open_files))
    
    def closeEvent(self, event: QCloseEvent):
        """关闭事件处理"""
        self._save_settings()
        event.accept()
    
    # ==================== 文件操作 ====================
    
    def _new_file(self):
        """新建文件"""
        self._editor_tabs.create_new_tab()
    
    def _open_file(self):
        """打开文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开文件", "",
            "Python files (*.py);;Text files (*.txt);;All files (*.*)"
        )
        if file_path:
            self._editor_tabs.open_file(file_path)
            self.file_opened.emit(file_path)
    
    def _open_folder(self):
        """打开文件夹"""
        folder_path = QFileDialog.getExistingDirectory(self, "打开文件夹")
        if folder_path:
            self._file_explorer.set_root_path(folder_path)
    
    def _save_file(self):
        """保存文件"""
        if self._editor_tabs.save_current_file():
            self._statusbar.showMessage("文件已保存", 3000)
    
    def _save_file_as(self):
        """另存为文件"""
        if self._editor_tabs.save_current_file_as():
            self._statusbar.showMessage("文件已保存", 3000)
    
    def _on_file_explorer_double_click(self, file_path: str):
        """文件浏览器双击处理"""
        if file_path.endswith('.py'):
            self._editor_tabs.open_file(file_path)
            self.file_opened.emit(file_path)
    
    def _on_file_saved(self, file_path: str):
        """文件保存处理"""
        self._statusbar.showMessage(f"已保存: {file_path}", 3000)
        self.file_saved.emit(file_path)
    
    # ==================== 编辑操作 ====================
    
    def _undo(self):
        """撤销"""
        editor = self._editor_tabs.get_current_editor()
        if editor:
            editor.undo()
    
    def _redo(self):
        """重做"""
        editor = self._editor_tabs.get_current_editor()
        if editor:
            editor.redo()
    
    def _cut(self):
        """剪切"""
        editor = self._editor_tabs.get_current_editor()
        if editor:
            editor.cut()
    
    def _copy(self):
        """复制"""
        editor = self._editor_tabs.get_current_editor()
        if editor:
            editor.copy()
    
    def _paste(self):
        """粘贴"""
        editor = self._editor_tabs.get_current_editor()
        if editor:
            editor.paste()
    
    # ==================== 运行操作 ====================
    
    def _run_code(self):
        """运行代码"""
        # 调用外部设置的运行动作
        if hasattr(self, '_run_action') and callable(self._run_action):
            self._run_action()
        else:
            self._statusbar.showMessage("运行功能未配置", 3000)
    
    def _debug_code(self):
        """调试代码"""
        # 调用外部设置的调试动作
        if hasattr(self, '_debug_action') and callable(self._debug_action):
            self._debug_action()
        else:
            self._statusbar.showMessage("调试功能未配置", 3000)
    
    # ==================== 视图操作 ====================
    
    def _change_theme(self, theme_name: str):
        """切换主题"""
        app = QApplication.instance()
        apply_theme(app, theme_name)
        self._statusbar.showMessage(f"主题已切换为: {theme_name}", 3000)
    
    # ==================== 帮助操作 ====================
    
    def _show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于 BBCode",
            "<h2>BBCode PyQt6 Edition</h2>"
            "<p>基于 PyQt6 的现代化 Python IDE</p>"
            "<p>版本: 2.0.0</p>"
            "<p>使用 PyQt6 构建，提供更现代的用户界面和更好的性能。</p>"
        )


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 应用主题
    apply_theme(app, "dark")
    
    # 创建主窗口
    window = QtWorkbench()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
