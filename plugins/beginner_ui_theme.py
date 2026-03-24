"""
适合编程初学者的简化UI主题
设计原则：简单、直观、友好
"""

from typing import Dict, Union

from thonny import get_workbench
from thonny.ui_utils import ems_to_pixels
from thonny.workbench import BasicUiThemeSettings, CompoundUiThemeSettings


def load_plugin():
    """加载适合初学者的UI主题"""
    get_workbench().add_ui_theme("beginner", "初学者主题", BeginnerUiTheme())


class BeginnerUiTheme(CompoundUiThemeSettings):
    """适合编程初学者的简化UI主题"""

    def __init__(self):
        super().__init__(
            {
                "*": self._global_settings(),
                "TFrame": self._frame_settings(),
                "TButton": self._button_settings(),
                "TLabel": self._label_settings(),
                "TEntry": self._entry_settings(),
                "TText": self._text_settings(),
                "TNotebook": self._notebook_settings(),
                "Treeview": self._treeview_settings(),
                "Vertical.TScrollbar": self._scrollbar_settings(),
                "Horizontal.TScrollbar": self._scrollbar_settings(),
            }
        )

    def _global_settings(self) -> BasicUiThemeSettings:
        """全局设置 - 使用更友好的配色方案"""
        return {
            "*": {
                "configure": {
                    "background": "#F8F9FA",  # 浅灰色背景
                    "foreground": "#2C3E50",  # 深蓝色文字
                    "font": ("Segoe UI", 10),
                }
            }
        }

    def _frame_settings(self) -> BasicUiThemeSettings:
        """框架设置 - 简化边框和间距"""
        return {
            "TFrame": {
                "configure": {
                    "background": "#F8F9FA",
                    "relief": "flat",  # 扁平化设计
                    "borderwidth": 0,
                }
            }
        }

    def _button_settings(self) -> BasicUiThemeSettings:
        """按钮设置 - 大按钮，圆角设计"""
        return {
            "TButton": {
                "configure": {
                    "background": "#3498DB",  # 蓝色按钮
                    "foreground": "white",
                    "font": ("Segoe UI", 10, "bold"),
                    "relief": "raised",
                    "borderwidth": 1,
                    "padx": ems_to_pixels(1.2),  # 更大的内边距
                    "pady": ems_to_pixels(0.5),
                },
                "map": {
                    "background": [
                        ("active", "#2980B9"),  # 鼠标悬停时变深
                        ("pressed", "#2471A3"),  # 按下时更深
                    ],
                },
            }
        }

    def _label_settings(self) -> BasicUiThemeSettings:
        """标签设置 - 清晰易读"""
        return {
            "TLabel": {
                "configure": {
                    "background": "#F8F9FA",
                    "foreground": "#2C3E50",
                    "font": ("Segoe UI", 10),
                }
            }
        }

    def _entry_settings(self) -> BasicUiThemeSettings:
        """输入框设置 - 清晰的边框"""
        return {
            "TEntry": {
                "configure": {
                    "background": "white",
                    "foreground": "#2C3E50",
                    "insertbackground": "#3498DB",  # 光标颜色
                    "relief": "sunken",
                    "borderwidth": 1,
                },
                "map": {
                    "background": [("focus", "#F0F8FF")],  # 聚焦时浅蓝色背景
                },
            }
        }

    def _text_settings(self) -> BasicUiThemeSettings:
        """文本框设置 - 适合代码编辑"""
        return {
            "TText": {
                "configure": {
                    "background": "white",
                    "foreground": "#2C3E50",
                    "insertbackground": "#3498DB",
                    "relief": "sunken",
                    "borderwidth": 1,
                    "selectbackground": "#3498DB",  # 选中背景色
                    "selectforeground": "white",
                }
            }
        }

    def _notebook_settings(self) -> BasicUiThemeSettings:
        """标签页设置 - 简化标签样式"""
        return {
            "TNotebook": {
                "configure": {
                    "background": "#ECF0F1",
                    "tabmargins": [ems_to_pixels(0.5), ems_to_pixels(0.2), ems_to_pixels(0.5), 0],
                }
            },
            "TNotebook.Tab": {
                "configure": {
                    "background": "#BDC3C7",
                    "foreground": "#2C3E50",
                    "padding": [ems_to_pixels(0.8), ems_to_pixels(0.3)],
                },
                "map": {
                    "background": [("selected", "#3498DB"), ("active", "#2980B9")],
                    "foreground": [("selected", "white")],
                },
            },
        }

    def _treeview_settings(self) -> BasicUiThemeSettings:
        """树形视图设置 - 简化样式"""
        return {
            "Treeview": {
                "configure": {
                    "background": "white",
                    "foreground": "#2C3E50",
                    "fieldbackground": "white",
                    "borderwidth": 0,
                },
                "map": {
                    "background": [("selected", "#3498DB")],
                    "foreground": [("selected", "white")],
                },
            },
            "Treeview.Heading": {
                "configure": {
                    "background": "#ECF0F1",
                    "foreground": "#2C3E50",
                    "relief": "flat",
                }
            },
        }

    def _scrollbar_settings(self) -> BasicUiThemeSettings:
        """滚动条设置 - 简化样式"""
        return {
            "Vertical.TScrollbar": {
                "configure": {
                    "background": "#BDC3C7",
                    "troughcolor": "#ECF0F1",
                    "borderwidth": 0,
                    "relief": "flat",
                }
            },
            "Horizontal.TScrollbar": {
                "configure": {
                    "background": "#BDC3C7",
                    "troughcolor": "#ECF0F1",
                    "borderwidth": 0,
                    "relief": "flat",
                }
            },
        }
