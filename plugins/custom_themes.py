"""
Custom Themes for BBCode - PyQt6版本
提供浅色主题和3套额外的可自定义主题选项
支持颜色方案、字体大小、界面布局等视觉元素的自定义
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QSpinBox, QTabWidget, QWidget,
    QFormLayout, QMessageBox, QListWidget, QColorDialog,
    QGroupBox, QScrollArea, QFrame, QGridLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from thonny import get_workbench
from thonny.misc_utils import running_on_windows
from thonny.ui_utils import scale
from thonny.workbench import UiThemeSettings


class ThemeConfig:
    """主题配置类"""
    
    def __init__(self, name: str, is_dark: bool = False):
        self.name = name
        self.is_dark = is_dark
        self.colors = {}
        self.fonts = {}
        self.layout = {}
        self._init_defaults()
    
    def _init_defaults(self):
        """初始化默认配置"""
        if self.is_dark:
            self.colors = {
                'bg_primary': '#1a1a2e',
                'bg_secondary': '#16213e',
                'bg_tertiary': '#0f3460',
                'bg_card': '#252542',
                'text_primary': '#eaeaea',
                'text_secondary': '#a0a0a0',
                'text_disabled': '#666666',
                'accent_primary': '#e94560',
                'accent_secondary': '#533483',
                'accent_success': '#4ecca3',
                'accent_warning': '#f9a825',
                'border_color': '#2d2d4a',
                'hover_bg': '#2a2a4a',
                'selected_bg': '#e94560',
            }
        else:
            self.colors = {
                'bg_primary': '#fafafa',
                'bg_secondary': '#ffffff',
                'bg_tertiary': '#f0f0f5',
                'bg_card': '#ffffff',
                'text_primary': '#2d3436',
                'text_secondary': '#636e72',
                'text_disabled': '#b2bec3',
                'accent_primary': '#6c5ce7',
                'accent_secondary': '#00b894',
                'accent_success': '#00b894',
                'accent_warning': '#fdcb6e',
                'border_color': '#dfe6e9',
                'hover_bg': '#f5f6fa',
                'selected_bg': '#6c5ce7',
            }
        
        self.fonts = {
            'default_family': 'Segoe UI' if running_on_windows() else 'Helvetica',
            'default_size': 10,
            'editor_family': 'Consolas',
            'editor_size': 12,
            'monospace_family': 'Consolas',
            'monospace_size': 10,
        }
        
        self.layout = {
            'border_width': 1,
            'padding_small': scale(5),
            'padding_medium': scale(10),
            'padding_large': scale(20),
            'scrollbar_width': scale(12),
            'button_padding_x': scale(15),
            'button_padding_y': scale(8),
        }
    
    def to_dict(self):
        """转换为字典"""
        return {
            'name': self.name,
            'is_dark': self.is_dark,
            'colors': self.colors,
            'fonts': self.fonts,
            'layout': self.layout,
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建"""
        config = cls(data.get('name', 'Custom'), data.get('is_dark', False))
        config.colors.update(data.get('colors', {}))
        config.fonts.update(data.get('fonts', {}))
        config.layout.update(data.get('layout', {}))
        return config


# 预定义主题配置
PREDEFINED_THEMES = {
    'ocean_breeze': {
        'name': 'Ocean Breeze',
        'is_dark': False,
        'colors': {
            'bg_primary': '#f0f9ff',
            'bg_secondary': '#ffffff',
            'bg_tertiary': '#e0f2fe',
            'bg_card': '#ffffff',
            'text_primary': '#0c4a6e',
            'text_secondary': '#0369a1',
            'text_disabled': '#94a3b8',
            'accent_primary': '#0ea5e9',
            'accent_secondary': '#06b6d4',
            'accent_success': '#10b981',
            'accent_warning': '#f59e0b',
            'border_color': '#bae6fd',
            'hover_bg': '#e0f2fe',
            'selected_bg': '#0ea5e9',
        }
    },
    'forest_calm': {
        'name': 'Forest Calm',
        'is_dark': False,
        'colors': {
            'bg_primary': '#f0fdf4',
            'bg_secondary': '#ffffff',
            'bg_tertiary': '#dcfce7',
            'bg_card': '#ffffff',
            'text_primary': '#14532d',
            'text_secondary': '#166534',
            'text_disabled': '#86efac',
            'accent_primary': '#22c55e',
            'accent_secondary': '#16a34a',
            'accent_success': '#15803d',
            'accent_warning': '#ca8a04',
            'border_color': '#bbf7d0',
            'hover_bg': '#dcfce7',
            'selected_bg': '#22c55e',
        }
    },
    'sunset_warm': {
        'name': 'Sunset Warm',
        'is_dark': False,
        'colors': {
            'bg_primary': '#fff7ed',
            'bg_secondary': '#ffffff',
            'bg_tertiary': '#ffedd5',
            'bg_card': '#ffffff',
            'text_primary': '#7c2d12',
            'text_secondary': '#9a3412',
            'text_disabled': '#fdba74',
            'accent_primary': '#f97316',
            'accent_secondary': '#ea580c',
            'accent_success': '#16a34a',
            'accent_warning': '#eab308',
            'border_color': '#fed7aa',
            'hover_bg': '#ffedd5',
            'selected_bg': '#f97316',
        }
    },
    'midnight_purple': {
        'name': 'Midnight Purple',
        'is_dark': True,
        'colors': {
            'bg_primary': '#1a1a2e',
            'bg_secondary': '#16213e',
            'bg_tertiary': '#0f3460',
            'bg_card': '#252542',
            'text_primary': '#eaeaea',
            'text_secondary': '#a0a0a0',
            'text_disabled': '#666666',
            'accent_primary': '#9d4edd',
            'accent_secondary': '#c77dff',
            'accent_success': '#4ecca3',
            'accent_warning': '#f9a825',
            'border_color': '#3d3d5c',
            'hover_bg': '#2a2a4a',
            'selected_bg': '#9d4edd',
        }
    },
}


def generate_theme_settings(config: ThemeConfig) -> UiThemeSettings:
    """根据主题配置生成UI主题设置"""
    c = config.colors
    l = config.layout
    
    return {
        ".": {
            "configure": {
                "foreground": c['text_primary'],
                "background": c['bg_primary'],
                "lightcolor": c['bg_primary'],
                "darkcolor": c['bg_primary'],
                "bordercolor": c['border_color'],
                "selectbackground": c['selected_bg'],
                "selectforeground": '#ffffff',
                "font": "TkDefaultFont",
            },
            "map": {
                "foreground": [("disabled", c['text_disabled']), ("active", c['text_primary'])],
                "background": [("disabled", c['bg_primary']), ("active", c['hover_bg'])],
                "selectbackground": [("!focus", c['bg_tertiary'])],
                "selectforeground": [("!focus", c['text_primary'])],
            },
        },
        "TNotebook": {
            "configure": {
                "bordercolor": c['border_color'],
                "tabmargins": [scale(1), 0, 0, 0],
                "padding": [0, 0, 0, 0],
            }
        },
        "ButtonNotebook.TNotebook": {"configure": {"bordercolor": c['bg_primary']}},
        "ViewNotebook.TNotebook": {"configure": {"bordercolor": c['bg_primary']}},
        "TNotebook.Tab": {
            "configure": {
                "background": c['bg_primary'],
                "bordercolor": c['border_color'],
                "padding": [scale(10), scale(5)],
            },
            "map": {
                "background": [
                    ("selected", c['bg_secondary']),
                    ("!selected", "!active", c['bg_primary']),
                    ("active", "!selected", c['hover_bg']),
                ],
                "bordercolor": [("selected", c['bg_primary']), ("!selected", c['border_color'])],
                "lightcolor": [("selected", c['bg_secondary']), ("!selected", c['bg_primary'])],
            },
        },
        "Treeview": {
            "configure": {
                "background": c['bg_secondary'],
                "borderwidth": 0,
                "relief": "flat",
                "rowheight": scale(22),
            },
            "map": {
                "background": [
                    ("selected", "focus", c['accent_primary']),
                    ("selected", "!focus", c['bg_tertiary']),
                ],
                "foreground": [
                    ("selected", "focus", "#ffffff"),
                    ("selected", "!focus", c['text_primary']),
                ],
            },
        },
        "Heading": {
            "configure": {
                "background": c['bg_tertiary'],
                "lightcolor": c['bg_tertiary'],
                "darkcolor": c['bg_tertiary'],
                "borderwidth": 0,
                "topmost_pixels_to_hide": 0,
                "font": "BoldTkDefaultFont",
            },
            "map": {
                "background": [
                    ("!active", c['bg_tertiary']),
                    ("active", c['hover_bg']),
                ]
            },
        },
        "TEntry": {
            "configure": {
                "fieldbackground": c['bg_secondary'],
                "lightcolor": c['bg_secondary'],
                "insertcolor": c['text_primary'],
                "borderwidth": 1,
                "relief": "solid",
            },
            "map": {
                "background": [("readonly", c['bg_secondary'])],
                "bordercolor": [("focus", c['accent_primary']), ("!focus", c['border_color'])],
                "lightcolor": [("focus", c['accent_primary'])],
            },
        },
        "TCombobox": {
            "configure": {
                "background": c['bg_secondary'],
                "fieldbackground": c['bg_secondary'],
                "selectbackground": c['bg_secondary'],
                "lightcolor": c['bg_secondary'],
                "darkcolor": c['bg_secondary'],
                "bordercolor": c['border_color'],
                "arrowcolor": c['text_primary'],
                "foreground": c['text_primary'],
                "selectforeground": c['text_primary'],
            },
            "map": {
                "background": [("active", c['bg_primary']), ("readonly", c['bg_primary'])],
                "bordercolor": [("focus", c['accent_primary']), ("!focus", c['border_color'])],
            },
        },
        "TScrollbar": {
            "configure": {
                "gripcount": 0,
                "borderwidth": 0,
                "padding": scale(2),
                "relief": "flat",
                "background": c['bg_tertiary'] if config.is_dark else "#c0c0c0",
                "darkcolor": c['bg_primary'],
                "lightcolor": c['bg_primary'],
                "bordercolor": c['bg_primary'],
                "troughcolor": c['bg_primary'],
                "arrowsize": scale(7),
                "width": l['scrollbar_width'],
            },
            "map": {
                "background": [
                    ("!disabled", c['bg_tertiary'] if config.is_dark else "#a0a0a0"),
                    ("disabled", c['bg_primary']),
                ],
            },
        },
        "TButton": {
            "configure": {
                "background": c['accent_primary'],
                "foreground": "#ffffff",
                "lightcolor": c['accent_primary'],
                "darkcolor": c['accent_primary'],
                "borderwidth": 0,
                "relief": "flat",
                "padding": [l['button_padding_x'], l['button_padding_y']],
                "font": "BoldTkDefaultFont",
            },
            "map": {
                "foreground": [("disabled", c['text_disabled'])],
                "background": [
                    ("pressed", c['accent_secondary']),
                    ("active", c['accent_secondary']),
                ],
                "lightcolor": [
                    ("pressed", c['accent_secondary']),
                    ("active", c['accent_secondary']),
                ],
                "darkcolor": [
                    ("pressed", c['accent_secondary']),
                    ("active", c['accent_secondary']),
                ],
            },
        },
        "TCheckbutton": {
            "configure": {
                "indicatorforeground": c['text_primary'],
                "indicatorbackground": c['bg_secondary'],
            },
            "map": {
                "indicatorforeground": [
                    ("disabled", "alternate", c['text_disabled']),
                    ("disabled", c['text_disabled']),
                ],
                "indicatorbackground": [
                    ("disabled", "alternate", c['bg_secondary']),
                    ("disabled", c['bg_secondary']),
                ],
            },
        },
        "TRadiobutton": {
            "configure": {
                "indicatorforeground": c['text_primary'],
                "indicatorbackground": c['bg_secondary'],
            },
            "map": {
                "indicatorforeground": [
                    ("disabled", "alternate", c['text_disabled']),
                    ("disabled", c['text_disabled']),
                ]
            },
        },
        "Toolbutton": {
            "configure": {"background": c['bg_primary']},
            "map": {"background": [("disabled", c['bg_primary']), ("active", c['hover_bg'])]},
        },
        "TLabel": {"configure": {"foreground": c['text_primary']}},
        "Url.TLabel": {"configure": {"foreground": c['accent_primary']}},
        "Tip.TLabel": {"configure": {"foreground": c['text_primary'], "background": c['bg_tertiary']}},
        "Tip.TFrame": {"configure": {"background": c['bg_tertiary']}},
        "Text": {
            "configure": {
                "background": c['bg_secondary'],
                "foreground": c['text_primary'],
                "insertbackground": c['accent_primary'],
                "selectbackground": c['accent_primary'],
                "selectforeground": "#ffffff",
            }
        },
        "Gutter": {
            "configure": {
                "background": c['bg_tertiary'] if config.is_dark else c['bg_primary'],
                "foreground": c['text_secondary'],
            }
        },
        "Listbox": {
            "configure": {
                "background": c['bg_secondary'],
                "foreground": c['text_primary'],
                "selectbackground": c['accent_primary'],
                "selectforeground": "#ffffff",
                "disabledforeground": c['text_disabled'],
                "highlightbackground": c['border_color'],
                "highlightcolor": c['accent_primary'],
                "highlightthickness": 0,
                "borderwidth": 0,
            }
        },
        "Menubar": {
            "configure": {
                "custom": running_on_windows(),
                "background": c['bg_primary'],
                "foreground": c['text_primary'],
                "activebackground": c['accent_primary'],
                "activeforeground": "#ffffff",
                "relief": "flat",
            }
        },
        "Menu": {
            "configure": {
                "background": c['bg_secondary'],
                "foreground": c['text_primary'],
                "selectcolor": c['text_primary'],
                "activebackground": c['accent_primary'],
                "activeforeground": "#ffffff",
                "relief": "flat",
                "borderwidth": 1,
            }
        },
        "TFrame": {"configure": {"background": c['bg_primary']}},
        "TProgressbar": {
            "configure": {
                "background": c['accent_primary'],
                "troughcolor": c['bg_tertiary'],
            }
        },
    }


class ThemeCustomizerDialog(QDialog):
    """主题自定义对话框 - PyQt6版本"""
    
    def __init__(self, parent=None, theme_config=None):
        super().__init__(parent)
        self.setWindowTitle("自定义主题")
        self.setMinimumSize(700, 600)
        
        self.theme_config = theme_config or ThemeConfig("自定义主题")
        self.color_buttons = {}
        
        self._setup_ui()
        self._load_theme()
    
    def _setup_ui(self):
        """创建UI界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel("自定义主题设置")
        title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        # 创建TabWidget
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # === 颜色设置页 ===
        color_page = QWidget()
        color_layout = QVBoxLayout(color_page)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QGridLayout(scroll_content)
        
        # 颜色类别
        color_categories = [
            ("背景颜色", [
                ('bg_primary', '主背景'),
                ('bg_secondary', '次背景'),
                ('bg_tertiary', '第三背景'),
                ('bg_card', '卡片背景'),
            ]),
            ("文字颜色", [
                ('text_primary', '主文字'),
                ('text_secondary', '次文字'),
                ('text_disabled', '禁用文字'),
            ]),
            ("强调颜色", [
                ('accent_primary', '主强调'),
                ('accent_secondary', '次强调'),
                ('accent_success', '成功色'),
                ('accent_warning', '警告色'),
            ]),
            ("其他颜色", [
                ('border_color', '边框颜色'),
                ('hover_bg', '悬停背景'),
                ('selected_bg', '选中背景'),
            ]),
        ]
        
        row = 0
        for category_name, colors in color_categories:
            # 类别标题
            cat_label = QLabel(category_name)
            cat_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            scroll_layout.addWidget(cat_label, row, 0, 1, 3)
            row += 1
            
            for color_key, color_name in colors:
                scroll_layout.addWidget(QLabel(f"{color_name}:"), row, 0)
                
                color_edit = QLineEdit()
                color_edit.setMaximumWidth(120)
                scroll_layout.addWidget(color_edit, row, 1)
                
                color_btn = QPushButton("选择")
                color_btn.setMaximumWidth(60)
                color_btn.clicked.connect(lambda checked, k=color_key, e=color_edit: self._choose_color(k, e))
                scroll_layout.addWidget(color_btn, row, 2)
                
                self.color_buttons[color_key] = (color_edit, color_btn)
                row += 1
        
        scroll_layout.setColumnStretch(3, 1)
        scroll.setWidget(scroll_content)
        color_layout.addWidget(scroll)
        tabs.addTab(color_page, "颜色")
        
        # === 字体设置页 ===
        font_page = QWidget()
        font_layout = QFormLayout(font_page)
        font_layout.setSpacing(10)
        
        # 字体选择
        self.default_font_combo = QComboBox()
        self.default_font_combo.addItems(["Segoe UI", "Helvetica", "Arial", "Consolas", "Courier New"])
        font_layout.addRow("默认字体:", self.default_font_combo)
        
        self.editor_font_combo = QComboBox()
        self.editor_font_combo.addItems(["Consolas", "Courier New", "Monospace"])
        font_layout.addRow("编辑器字体:", self.editor_font_combo)
        
        self.monospace_font_combo = QComboBox()
        self.monospace_font_combo.addItems(["Consolas", "Courier New", "Monospace"])
        font_layout.addRow("等宽字体:", self.monospace_font_combo)
        
        # 字体大小
        self.default_size_spin = QSpinBox()
        self.default_size_spin.setRange(8, 20)
        font_layout.addRow("默认字号:", self.default_size_spin)
        
        self.editor_size_spin = QSpinBox()
        self.editor_size_spin.setRange(8, 32)
        font_layout.addRow("编辑器字号:", self.editor_size_spin)
        
        self.monospace_size_spin = QSpinBox()
        self.monospace_size_spin.setRange(8, 20)
        font_layout.addRow("等宽字号:", self.monospace_size_spin)
        
        tabs.addTab(font_page, "字体")
        
        # === 布局设置页 ===
        layout_page = QWidget()
        layout_form = QFormLayout(layout_page)
        layout_form.setSpacing(10)
        
        self.border_width_spin = QSpinBox()
        self.border_width_spin.setRange(0, 5)
        layout_form.addRow("边框宽度:", self.border_width_spin)
        
        self.scrollbar_width_spin = QSpinBox()
        self.scrollbar_width_spin.setRange(8, 20)
        layout_form.addRow("滚动条宽度:", self.scrollbar_width_spin)
        
        tabs.addTab(layout_page, "布局")
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        preview_btn = QPushButton("预览")
        preview_btn.clicked.connect(self._preview_theme)
        btn_layout.addWidget(preview_btn)
        
        import_btn = QPushButton("导入预设")
        import_btn.clicked.connect(self._import_preset)
        btn_layout.addWidget(import_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("保存")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self._save_theme)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
    
    def _choose_color(self, color_key: str, color_edit: QLineEdit):
        """选择颜色"""
        color = QColorDialog.getColor(QColor(color_edit.text()), self)
        if color.isValid():
            color_edit.setText(color.name())
    
    def _load_theme(self):
        """加载主题配置"""
        # 加载颜色
        for key, (edit, btn) in self.color_buttons.items():
            if key in self.theme_config.colors:
                edit.setText(self.theme_config.colors[key])
        
        # 加载字体
        self.default_font_combo.setCurrentText(self.theme_config.fonts.get('default_family', 'Segoe UI'))
        self.editor_font_combo.setCurrentText(self.theme_config.fonts.get('editor_family', 'Consolas'))
        self.monospace_font_combo.setCurrentText(self.theme_config.fonts.get('monospace_family', 'Consolas'))
        
        self.default_size_spin.setValue(self.theme_config.fonts.get('default_size', 10))
        self.editor_size_spin.setValue(self.theme_config.fonts.get('editor_size', 12))
        self.monospace_size_spin.setValue(self.theme_config.fonts.get('monospace_size', 10))
        
        # 加载布局
        self.border_width_spin.setValue(self.theme_config.layout.get('border_width', 1))
        self.scrollbar_width_spin.setValue(self.theme_config.layout.get('scrollbar_width', 12))
    
    def _preview_theme(self):
        """预览主题"""
        QMessageBox.information(self, "预览", "主题预览功能将在保存后生效")
    
    def _import_preset(self):
        """导入预设主题"""
        dialog = QDialog(self)
        dialog.setWindowTitle("选择预设主题")
        dialog.setMinimumSize(300, 250)
        
        layout = QVBoxLayout(dialog)
        
        layout.addWidget(QLabel("选择预设主题:"))
        
        list_widget = QListWidget()
        for key in PREDEFINED_THEMES.keys():
            list_widget.addItem(PREDEFINED_THEMES[key]['name'])
        layout.addWidget(list_widget)
        
        btn = QPushButton("应用")
        btn.clicked.connect(lambda: self._apply_preset(list_widget, dialog))
        layout.addWidget(btn)
        
        dialog.exec()
    
    def _apply_preset(self, list_widget: QListWidget, dialog: QDialog):
        """应用预设"""
        item = list_widget.currentItem()
        if item:
            preset_name = item.text()
            for key, preset in PREDEFINED_THEMES.items():
                if preset['name'] == preset_name:
                    self.theme_config = ThemeConfig.from_dict(preset)
                    self._load_theme()
                    break
        dialog.accept()
    
    def _update_theme_config(self):
        """更新主题配置"""
        # 更新颜色
        for key, (edit, btn) in self.color_buttons.items():
            self.theme_config.colors[key] = edit.text()
        
        # 更新字体
        self.theme_config.fonts['default_family'] = self.default_font_combo.currentText()
        self.theme_config.fonts['editor_family'] = self.editor_font_combo.currentText()
        self.theme_config.fonts['monospace_family'] = self.monospace_font_combo.currentText()
        
        self.theme_config.fonts['default_size'] = self.default_size_spin.value()
        self.theme_config.fonts['editor_size'] = self.editor_size_spin.value()
        self.theme_config.fonts['monospace_size'] = self.monospace_size_spin.value()
        
        # 更新布局
        self.theme_config.layout['border_width'] = self.border_width_spin.value()
        self.theme_config.layout['scrollbar_width'] = self.scrollbar_width_spin.value()
    
    def _save_theme(self):
        """保存主题"""
        self._update_theme_config()
        
        # 保存到工作区配置
        wb = get_workbench()
        theme_name = self.theme_config.name
        
        # 保存主题配置
        wb.set_option(f"custom_themes.{theme_name}", self.theme_config.to_dict())
        
        # 注册主题
        register_custom_theme(self.theme_config)
        
        QMessageBox.information(self, "成功", f"主题 '{theme_name}' 已保存并应用")
        self.accept()


def register_custom_theme(config: ThemeConfig):
    """注册自定义主题"""
    workbench = get_workbench()
    theme_settings = generate_theme_settings(config)
    
    workbench.add_ui_theme(
        config.name,
        "Enhanced Clam",
        lambda: theme_settings,
    )


def load_custom_themes():
    """加载所有自定义主题"""
    wb = get_workbench()
    
    # 加载预设主题
    for key, preset in PREDEFINED_THEMES.items():
        config = ThemeConfig.from_dict(preset)
        register_custom_theme(config)
    
    # 加载用户保存的自定义主题
    try:
        custom_themes = wb.get_option("custom_themes", {})
        for theme_name, theme_data in custom_themes.items():
            if theme_name not in [p['name'] for p in PREDEFINED_THEMES.values()]:
                config = ThemeConfig.from_dict(theme_data)
                register_custom_theme(config)
    except:
        pass


def open_theme_customizer():
    """打开主题自定义对话框"""
    from thonny import get_workbench
    dialog = ThemeCustomizerDialog(get_workbench())
    dialog.exec()


def load_plugin():
    """加载插件"""
    workbench = get_workbench()
    
    # 加载自定义主题
    load_custom_themes()
    
    # 添加主题自定义命令
    workbench.add_command(
        "customize_theme",
        "view",
        "自定义主题...",
        open_theme_customizer,
        group=50,
    )
    
    # 添加预设主题切换命令
    for key, preset in PREDEFINED_THEMES.items():
        workbench.add_command(
            f"set_theme_{key}",
            "view",
            f"主题: {preset['name']}",
            lambda k=key: _apply_preset_theme(k),
            group=51,
        )


def _apply_preset_theme(preset_key: str):
    """应用预设主题"""
    if preset_key in PREDEFINED_THEMES:
        preset = PREDEFINED_THEMES[preset_key]
        wb = get_workbench()
        wb.set_option("view.ui_theme", preset['name'])
        wb.reload_themes()
