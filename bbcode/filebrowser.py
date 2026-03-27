# -*- coding: utf-8 -*-
"""
BBCode 文件浏览器组件
"""

from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeView, QLabel,
    QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFileSystemModel


class FileExplorer(QWidget):
    """文件浏览器组件"""
    
    file_selected = pyqtSignal(str)
    file_double_clicked = pyqtSignal(str)
    root_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_root = str(Path.home())
        self._setup_ui()
        self.set_root_path(self._current_root)
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 工具栏
        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(8, 4, 8, 4)
        toolbar.setSpacing(4)
        
        self._up_btn = QPushButton("⬆ 上一级")
        self._up_btn.setFixedHeight(28)
        self._up_btn.clicked.connect(self._go_to_parent)
        toolbar.addWidget(self._up_btn)
        
        self._path_label = QLabel()
        self._path_label.setStyleSheet("color: #888; font-size: 11px;")
        self._path_label.setWordWrap(True)
        toolbar.addWidget(self._path_label, 1)
        
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
        
        self._tree.setColumnWidth(0, 250)
        self._tree.setColumnHidden(1, True)
        self._tree.setColumnHidden(2, True)
        self._tree.setColumnHidden(3, True)
        self._tree.setSortingEnabled(True)
        self._tree.setSelectionMode(QTreeView.SelectionMode.SingleSelection)
        
        self._tree.clicked.connect(self._on_item_clicked)
        self._tree.doubleClicked.connect(self._on_item_double_clicked)
        
        layout.addWidget(self._tree)
    
    def _go_to_parent(self):
        parent = Path(self._current_root).parent
        if parent.exists():
            self.set_root_path(str(parent))
    
    def _refresh(self):
        self._model.setRootPath('')
        self.set_root_path(self._current_root)
    
    def _update_path_label(self):
        path = Path(self._current_root)
        try:
            short_path = path.relative_to(Path.home())
            display = f"~/{short_path}"
        except ValueError:
            display = str(path)
        
        if len(display) > 40:
            parts = display.split('/')
            if len(parts) > 2:
                display = ".../" + "/".join(parts[-2:])
        
        self._path_label.setText(display)
        self._path_label.setToolTip(self._current_root)
    
    def set_root_path(self, path: str):
        self._current_root = path
        self._tree.setRootIndex(self._model.index(path))
        self._update_path_label()
        self.root_changed.emit(path)
        
        parent = Path(path).parent
        self._up_btn.setEnabled(parent.exists() and parent != Path(path))
    
    def get_current_root(self) -> str:
        return self._current_root
    
    def get_selected_path(self) -> Optional[str]:
        indexes = self._tree.selectedIndexes()
        if indexes:
            return self._model.filePath(indexes[0])
        return None
    
    def _on_item_clicked(self, index):
        path = self._model.filePath(index)
        self.file_selected.emit(path)
    
    def _on_item_double_clicked(self, index):
        path = self._model.filePath(index)
        if self._model.isDir(index):
            self.set_root_path(path)
        else:
            self.file_double_clicked.emit(path)
