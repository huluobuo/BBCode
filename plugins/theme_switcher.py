"""
BBCode 主题切换器 - 应用内主题切换
支持快速切换和预览主题
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QFrame, QSplitter,
    QWidget, QGridLayout, QRadioButton, QButtonGroup,
    QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPalette

from thonny import get_workbench
from plugins.custom_themes import PREDEFINED_THEMES, ThemeConfig, generate_theme_settings


class ThemePreviewWidget(QFrame):
    """主题预览组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setMinimumSize(300, 200)
        self._setup_ui()
    
    def _setup_ui(self):
        """设置预览UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # 标题
        title = QLabel("主题预览")
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # 示例组件容器
        self.preview_container = QFrame()
        preview_layout = QVBoxLayout(self.preview_container)
        preview_layout.setSpacing(10)
        
        # 示例按钮
        self.sample_button = QPushButton("示例按钮")
        preview_layout.addWidget(self.sample_button)
        
        # 示例标签
        self.sample_label = QLabel("示例文本标签")
        preview_layout.addWidget(self.sample_label)
        
        # 示例输入框
        self.sample_input = QLabel("输入框示例")
        self.sample_input.setFrameStyle(QFrame.Shape.StyledPanel)
        self.sample_input.setMinimumHeight(30)
        preview_layout.addWidget(self.sample_input)
        
        preview_layout.addStretch()
        layout.addWidget(self.preview_container)
        layout.addStretch()
    
    def update_preview(self, config: ThemeConfig):
        """更新预览"""
        c = config.colors
        
        # 更新背景色
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {c['bg_primary']};
                color: {c['text_primary']};
            }}
            QLabel {{
                color: {c['text_primary']};
            }}
            QPushButton {{
                background-color: {c['accent_primary']};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {c['accent_secondary']};
            }}
        """)


class ThemeSwitcherDialog(QDialog):
    """主题切换对话框 - 支持应用内切换"""
    
    theme_changed = pyqtSignal(str)  # 主题变更信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("切换主题")
        self.setMinimumSize(600, 450)
        
        self._current_theme = None
        self._setup_ui()
        self._load_current_theme()
    
    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title = QLabel("选择主题")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # 分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧：主题列表
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # 浅色主题组
        light_group = QFrame()
        light_layout = QVBoxLayout(light_group)
        light_layout.setContentsMargins(10, 10, 10, 10)
        light_layout.setSpacing(5)
        
        light_title = QLabel("浅色主题")
        light_title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        light_layout.addWidget(light_title)
        
        self.light_buttons = QButtonGroup(self)
        for key, preset in PREDEFINED_THEMES.items():
            if not preset['is_dark']:
                radio = QRadioButton(preset['name'])
                radio.setProperty('theme_key', key)
                self.light_buttons.addButton(radio)
                light_layout.addWidget(radio)
        
        left_layout.addWidget(light_group)
        
        # 深色主题组
        dark_group = QFrame()
        dark_layout = QVBoxLayout(dark_group)
        dark_layout.setContentsMargins(10, 10, 10, 10)
        dark_layout.setSpacing(5)
        
        dark_title = QLabel("深色主题")
        dark_title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        dark_layout.addWidget(dark_title)
        
        self.dark_buttons = QButtonGroup(self)
        for key, preset in PREDEFINED_THEMES.items():
            if preset['is_dark']:
                radio = QRadioButton(preset['name'])
                radio.setProperty('theme_key', key)
                self.dark_buttons.addButton(radio)
                dark_layout.addWidget(radio)
        
        left_layout.addWidget(dark_group)
        left_layout.addStretch()
        
        # 连接信号
        self.light_buttons.buttonClicked.connect(self._on_theme_selected)
        self.dark_buttons.buttonClicked.connect(self._on_theme_selected)
        
        splitter.addWidget(left_widget)
        
        # 右侧：预览
        self.preview = ThemePreviewWidget()
        splitter.addWidget(self.preview)
        
        splitter.setSizes([250, 350])
        layout.addWidget(splitter)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        apply_btn = QPushButton("应用")
        apply_btn.setDefault(True)
        apply_btn.clicked.connect(self._apply_theme)
        btn_layout.addWidget(apply_btn)
        
        layout.addLayout(btn_layout)
    
    def _load_current_theme(self):
        """加载当前主题"""
        wb = get_workbench()
        current_theme = wb.get_option("view.ui_theme", "Modern Light")
        
        # 查找并选中当前主题
        for button in self.light_buttons.buttons():
            key = button.property('theme_key')
            if PREDEFINED_THEMES.get(key, {}).get('name') == current_theme:
                button.setChecked(True)
                self._preview_theme(key)
                return
        
        for button in self.dark_buttons.buttons():
            key = button.property('theme_key')
            if PREDEFINED_THEMES.get(key, {}).get('name') == current_theme:
                button.setChecked(True)
                self._preview_theme(key)
                return
    
    def _on_theme_selected(self, button):
        """主题被选中"""
        key = button.property('theme_key')
        self._preview_theme(key)
    
    def _preview_theme(self, key: str):
        """预览主题"""
        if key in PREDEFINED_THEMES:
            preset = PREDEFINED_THEMES[key]
            config = ThemeConfig.from_dict(preset)
            self.preview.update_preview(config)
            self._current_theme = key
    
    def _apply_theme(self):
        """应用主题"""
        if self._current_theme:
            self._apply_preset_theme(self._current_theme)
            self.theme_changed.emit(self._current_theme)
            self.accept()
        else:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "提示", "请先选择一个主题")
    
    def _apply_preset_theme(self, preset_key: str):
        """应用预设主题"""
        if preset_key in PREDEFINED_THEMES:
            preset = PREDEFINED_THEMES[preset_key]
            wb = get_workbench()
            wb.set_option("view.ui_theme", preset['name'])
            wb.reload_themes()


def open_theme_switcher():
    """打开主题切换对话框"""
    from thonny import get_workbench
    dialog = ThemeSwitcherDialog(get_workbench())
    dialog.exec()


def load_plugin():
    """加载插件"""
    from thonny import get_workbench
    
    # 添加主题切换命令到视图菜单
    get_workbench().add_command(
        "switch_theme",
        "view",
        "切换主题...",
        open_theme_switcher,
        group=45,  # 在自定义主题之前
    )


if __name__ == "__main__":
    # 测试代码
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    dialog = ThemeSwitcherDialog()
    dialog.exec()
    sys.exit(app.exec())
