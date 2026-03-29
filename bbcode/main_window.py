# -*- coding: utf-8 -*-
"""
BBCode 主窗口
整合编辑器、文件浏览器、AI聊天、终端
"""

import sys
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QMenuBar, QMenu, QToolBar, QStatusBar, QSplitter, QTabWidget,
    QTextEdit, QTreeView, QDockWidget, QLabel,
    QPushButton, QLineEdit, QComboBox, QMessageBox, QProgressBar,
    QFrame, QFileDialog, QInputDialog, QToolButton, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QSize, QSettings
from PyQt6.QtGui import QAction, QIcon, QFont, QKeySequence, QCloseEvent, QFileSystemModel

from bbcode.editor import CodeEditor, EditorTabWidget
from bbcode.filebrowser import FileExplorer
from bbcode.terminal import Terminal
from bbcode.ai_chat import AIChat
from bbcode.splash_screen import show_splash_screen
from bbcode.settings_dialog import SettingsDialog
from bbcode.logger import get_logger

# 获取日志记录器
log = get_logger("MainWindow")


class MainWindow(QMainWindow):
    """BBCode 主窗口"""
    
    def __init__(self):
        super().__init__()
        
        log.info("初始化主窗口...")
        
        self.setWindowTitle("BBCode - Python IDE")
        self.setGeometry(100, 100, 1600, 1000)
        
        self._settings = QSettings("BBCode", "IDE")
        
        self._setup_ui()
        self._setup_menu()
        self._setup_toolbar()
        self._setup_statusbar()
        self._setup_dock_widgets()
        
        self._load_settings()
        
        log.info("主窗口初始化完成")
    
    def _setup_ui(self):
        """设置主UI"""
        # 中央分割器
        self._central_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(self._central_splitter)
        
        # 编辑器标签页
        self._editor_tabs = EditorTabWidget()
        self._editor_tabs.file_saved.connect(self._on_file_saved)
        self._central_splitter.addWidget(self._editor_tabs)
        
        # 设置分割器比例
        self._central_splitter.setSizes([1200, 400])
        
        # 创建默认编辑器
        self._editor_tabs.create_new_tab()
    
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
        
        # 视图菜单
        view_menu = menubar.addMenu("视图(&V)")
        
        self._show_file_explorer_action = QAction("文件浏览器", self)
        self._show_file_explorer_action.setCheckable(True)
        self._show_file_explorer_action.setChecked(True)
        view_menu.addAction(self._show_file_explorer_action)
        
        # 设置菜单
        settings_menu = menubar.addMenu("设置(&S)")
        
        settings_action = QAction("首选项...", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self._show_settings)
        settings_menu.addAction(settings_action)
        
        self._show_ai_chat_action = QAction("AI 助手", self)
        self._show_ai_chat_action.setCheckable(True)
        self._show_ai_chat_action.setChecked(True)
        view_menu.addAction(self._show_ai_chat_action)
        
        self._show_terminal_action = QAction("终端", self)
        self._show_terminal_action.setCheckable(True)
        self._show_terminal_action.setChecked(True)
        view_menu.addAction(self._show_terminal_action)
        
        view_menu.addSeparator()
        
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
        toolbar.setObjectName("mainToolbar")
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #2d2d30;
                border: none;
                spacing: 5px;
                padding: 5px;
            }
            QToolButton {
                background-color: transparent;
                border: none;
                padding: 5px;
                border-radius: 4px;
            }
            QToolButton:hover {
                background-color: #3c3c3c;
            }
            QToolButton:pressed {
                background-color: #007acc;
            }
        """)
        self.addToolBar(toolbar)
        
        # 文件操作
        new_action = QAction(QIcon("res/new-file.png"), "新建", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self._new_file)
        toolbar.addAction(new_action)
        
        open_action = QAction(QIcon("res/open-file.png"), "打开", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._open_file)
        toolbar.addAction(open_action)
        
        save_action = QAction(QIcon("res/save-file.png"), "保存", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self._save_file)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        # 运行操作
        run_action = QAction(QIcon("res/run-current-script.png"), "运行", self)
        run_action.triggered.connect(self._run_code)
        toolbar.addAction(run_action)
        
        toolbar.addSeparator()
        
        # 后端选择
        toolbar.addWidget(QLabel("后端: "))
        
        self._backend_combo = QComboBox()
        self._backend_combo.addItems(["Local Python", "MicroPython", "CircuitPython"])
        self._backend_combo.setFixedWidth(150)
        toolbar.addWidget(self._backend_combo)
    
    def _setup_statusbar(self):
        """设置状态栏"""
        self._statusbar = QStatusBar()
        self.setStatusBar(self._statusbar)
        
        self._statusbar.showMessage("就绪")
        
        # 行列指示器
        self._position_label = QLabel("行 1, 列 1")
        self._statusbar.addPermanentWidget(self._position_label)
    
    def _setup_dock_widgets(self):
        """设置停靠窗口"""
        # 文件浏览器
        self._file_explorer = FileExplorer()
        self._file_dock = QDockWidget("文件浏览器", self)
        self._file_dock.setObjectName("fileDock")
        self._file_dock.setWidget(self._file_explorer)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self._file_dock)
        
        self._file_explorer.file_double_clicked.connect(self._on_file_explorer_double_click)
        self._show_file_explorer_action.triggered.connect(self._file_dock.setVisible)
        self._file_dock.visibilityChanged.connect(self._show_file_explorer_action.setChecked)
        
        # AI 聊天
        self._ai_chat = AIChat()
        self._ai_dock = QDockWidget("AI 助手", self)
        self._ai_dock.setObjectName("aiDock")
        self._ai_dock.setWidget(self._ai_chat)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self._ai_dock)
        
        self._show_ai_chat_action.triggered.connect(self._ai_dock.setVisible)
        self._ai_dock.visibilityChanged.connect(self._show_ai_chat_action.setChecked)
        
        # 终端
        self._terminal = Terminal()
        self._terminal_dock = QDockWidget("终端", self)
        self._terminal_dock.setObjectName("terminalDock")
        self._terminal_dock.setWidget(self._terminal)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self._terminal_dock)
        
        self._show_terminal_action.triggered.connect(self._terminal_dock.setVisible)
        self._terminal_dock.visibilityChanged.connect(self._show_terminal_action.setChecked)
    
    def _reset_layout(self):
        """重置布局"""
        self._file_dock.setVisible(True)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self._file_dock)
        
        self._ai_dock.setVisible(True)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self._ai_dock)
        
        self._terminal_dock.setVisible(True)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self._terminal_dock)
        
        self._central_splitter.setSizes([1200, 400])
        
        self._statusbar.showMessage("布局已重置", 3000)
    
    def _load_settings(self):
        """加载设置"""
        geometry = self._settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
        state = self._settings.value("windowState")
        if state:
            self.restoreState(state)
        
        last_folder = self._settings.value("lastFolder")
        if last_folder and Path(last_folder).exists():
            self._file_explorer.set_root_path(last_folder)
        
        open_files = self._settings.value("openFiles")
        if open_files:
            files = open_files.split(";")
            for file_path in files:
                if Path(file_path).exists():
                    self._editor_tabs.open_file(file_path)
    
    def _save_settings(self):
        """保存设置"""
        self._settings.setValue("geometry", self.saveGeometry())
        self._settings.setValue("windowState", self.saveState())
        
        current_root = self._file_explorer.get_current_root()
        self._settings.setValue("lastFolder", current_root)
        
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
        log.info("应用程序关闭")
        self._save_settings()
        event.accept()
    
    # ==================== 文件操作 ====================
    
    def _new_file(self):
        """新建文件"""
        log.info("创建新文件")
        self._editor_tabs.create_new_tab()
    
    def _open_file(self):
        """打开文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开文件", "",
            "Python files (*.py);;"
            "Text files (*.txt);;"
            "JSON files (*.json);;"
            "CSV files (*.csv);;"
            "Batch files (*.bat *.cmd);;"
            "PowerShell files (*.ps1);;"
            "Markdown files (*.md);;"
            "XML files (*.xml);;"
            "YAML files (*.yaml *.yml);;"
            "Config files (*.ini *.cfg);;"
            "Log files (*.log);;"
            "Image files (*.png *.jpg *.jpeg *.gif *.bmp);;"
            "Audio files (*.mp3 *.wav);;"
            "Video files (*.mp4 *.avi *.mkv);;"
            "All files (*.*)"
        )
        if file_path:
            log.info(f"打开文件: {file_path}")
            self._editor_tabs.open_file(file_path)
    
    def _open_folder(self):
        """打开文件夹"""
        folder_path = QFileDialog.getExistingDirectory(self, "打开文件夹")
        if folder_path:
            self._file_explorer.set_root_path(folder_path)
    
    def _save_file(self):
        """保存文件"""
        if self._editor_tabs.save_current_file():
            log.info("文件已保存")
            self._statusbar.showMessage("文件已保存", 3000)
    
    def _save_file_as(self):
        """另存为文件"""
        if self._editor_tabs.save_current_file_as():
            self._statusbar.showMessage("文件已保存", 3000)
    
    def _on_file_explorer_double_click(self, file_path: str):
        """文件浏览器双击处理"""
        # 支持的可编辑文件类型
        editable_extensions = {'.py', '.txt', '.json', '.csv', '.bat', '.cmd', '.ps1', '.md', '.xml', '.yaml', '.yml', '.ini', '.cfg', '.log'}
        # 媒体文件类型（可以查看但不一定能编辑）
        media_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.mp3', '.wav', '.mp4', '.avi', '.mkv'}
        
        file_ext = Path(file_path).suffix.lower()
        if file_ext in editable_extensions:
            self._editor_tabs.open_file(file_path)
        elif file_ext in media_extensions:
            # 媒体文件显示提示，未来可以添加预览功能
            self._statusbar.showMessage(f"媒体文件: {file_path} (预览功能开发中)", 5000)
    
    def _on_file_saved(self, file_path: str):
        """文件保存处理"""
        self._statusbar.showMessage(f"已保存: {file_path}", 3000)
    
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
        editor = self._editor_tabs.get_current_editor()
        if editor:
            code = editor.get_text()
            # 获取当前标签页关联的临时文件路径
            temp_file = self._editor_tabs.get_current_temp_file()
            self._terminal.execute_code(code, temp_file)
            # 更新标签页tooltip显示执行的文件
            if temp_file:
                self._editor_tabs.setTabToolTip(self._editor_tabs.currentIndex(), f"临时文件: {temp_file}")
            self._statusbar.showMessage("代码已发送到终端执行", 3000)
    
    # ==================== 设置操作 ====================
    
    def _show_settings(self):
        """显示设置对话框"""
        log.info("打开设置对话框")
        dialog = SettingsDialog(self)
        dialog.exec()
    
    # ==================== 帮助操作 ====================
    
    def _show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于 BBCode",
            "<h2>BBCode Python IDE</h2>"
            "<p>基于 PyQt6 的现代化 Python IDE</p>"
            "<p>版本: 2.0.2.1</p>"
        )


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用程序图标
    app_icon = QIcon("res/bbc.png")
    app.setWindowIcon(app_icon)
    
    # 显示启动动画
    splash = show_splash_screen(app)
    
    # 设置应用样式
    app.setStyle("Fusion")
    
    # 设置深色主题
    app.setStyleSheet("""
        QMainWindow {
            background-color: #1e1e1e;
        }
        QMenuBar {
            background-color: #2d2d30;
            color: #d4d4d4;
        }
        QMenuBar::item:selected {
            background-color: #3c3c3c;
        }
        QMenu {
            background-color: #2d2d30;
            color: #d4d4d4;
            border: 1px solid #3c3c3c;
        }
        QMenu::item:selected {
            background-color: #007acc;
        }
        QToolBar {
            background-color: #2d2d30;
            border: none;
            spacing: 5px;
            padding: 5px;
        }
        QPushButton {
            background-color: #3c3c3c;
            color: #d4d4d4;
            border: 1px solid #555;
            padding: 5px 15px;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #4c4c4c;
        }
        QPushButton:pressed {
            background-color: #007acc;
        }
        QComboBox {
            background-color: #3c3c3c;
            color: #d4d4d4;
            border: 1px solid #555;
            padding: 5px;
        }
        QStatusBar {
            background-color: #007acc;
            color: white;
        }
        QDockWidget {
            color: #d4d4d4;
        }
        QDockWidget::title {
            background-color: #2d2d30;
            padding: 5px;
        }
        QTabWidget::pane {
            background-color: #1e1e1e;
            border: 1px solid #3c3c3c;
        }
        QTabBar::tab {
            background-color: #2d2d30;
            color: #d4d4d4;
            padding: 8px 16px;
            border: 1px solid #3c3c3c;
        }
        QTabBar::tab:selected {
            background-color: #1e1e1e;
            border-bottom: 2px solid #007acc;
        }
        QTabBar::tab:hover {
            background-color: #3c3c3c;
        }
        QTreeView {
            background-color: #1e1e1e;
            color: #d4d4d4;
            border: none;
        }
        QTreeView::item:selected {
            background-color: #007acc;
        }
        QTreeView::item:hover {
            background-color: #2d2d30;
        }
        QScrollArea {
            border: none;
        }
    """)
    
    # 创建主窗口（不立即显示）
    window = MainWindow()
    
    # 连接启动动画完成信号到主窗口显示
    splash.finished.connect(window.show)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
