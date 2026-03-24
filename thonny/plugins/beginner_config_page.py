"""
适合编程初学者的简化配置页面
"""

import tkinter as tk
from tkinter import ttk
from typing import List

from thonny import get_workbench
from thonny.config_ui import ConfigurationPage
from thonny.languages import tr
from thonny.ui_utils import ems_to_pixels


class BeginnerConfigPage(ConfigurationPage):
    """适合初学者的简化配置页面"""

    def __init__(self, master):
        super().__init__(master)

        # 创建友好的配置界面
        self._create_theme_section()
        self._create_ai_assistant_section()
        self._create_editor_section()

        self.columnconfigure(1, weight=1)
        self.rowconfigure(10, weight=1)

    def _create_theme_section(self):
        """创建主题配置部分"""
        # 主题标题
        theme_label = self._create_section_label("🎨 界面主题")
        theme_label.grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(ems_to_pixels(1), ems_to_pixels(0.5))
        )

        # 主题选择
        theme_frame = self._create_option_frame("选择适合初学者的界面风格:")
        theme_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, ems_to_pixels(1)))

        # 初学者主题选项
        self.beginner_theme_var = tk.BooleanVar(
            value=get_workbench().get_option("ui.theme", "") == "beginner"
        )
        beginner_theme_check = ttk.Checkbutton(
            theme_frame,
            text="使用初学者友好主题",
            variable=self.beginner_theme_var,
            command=self._toggle_beginner_theme,
        )
        beginner_theme_check.pack(anchor="w", padx=ems_to_pixels(1))

        # 主题说明
        theme_desc = tk.Label(
            theme_frame,
            text="• 简化界面布局\n• 更大的按钮和字体\n• 友好的配色方案",
            justify="left",
            background=self._get_background(),
            foreground="#666666",
            font="Segoe UI 9",
        )
        theme_desc.pack(anchor="w", padx=ems_to_pixels(2), pady=(ems_to_pixels(0.3), 0))

    def _create_ai_assistant_section(self):
        """创建AI助手配置部分"""
        # AI助手标题
        ai_label = self._create_section_label("🤖 AI编程助手")
        ai_label.grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(ems_to_pixels(1), ems_to_pixels(0.5))
        )

        # AI助手配置
        ai_frame = self._create_option_frame("配置AI助手设置:")
        ai_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, ems_to_pixels(1)))

        # 默认打开AI助手
        self.auto_open_ai_var = tk.BooleanVar(
            value=get_workbench().get_option("assistance.auto_open_ai", True)
        )
        auto_open_check = ttk.Checkbutton(
            ai_frame, text="启动时自动打开AI编程助手", variable=self.auto_open_ai_var
        )
        auto_open_check.pack(anchor="w", padx=ems_to_pixels(1))

        # AI助手说明
        ai_desc = tk.Label(
            ai_frame,
            text="• 启动时自动显示AI助手页面\n• 方便随时提问编程问题\n• 使用gemma3:1b模型",
            justify="left",
            background=self._get_background(),
            foreground="#666666",
            font="Segoe UI 9",
        )
        ai_desc.pack(anchor="w", padx=ems_to_pixels(2), pady=(ems_to_pixels(0.3), 0))

    def _create_editor_section(self):
        """创建编辑器配置部分"""
        # 编辑器标题
        editor_label = self._create_section_label("📝 代码编辑器")
        editor_label.grid(
            row=4, column=0, columnspan=2, sticky="w", pady=(ems_to_pixels(1), ems_to_pixels(0.5))
        )

        # 编辑器配置
        editor_frame = self._create_option_frame("编辑器显示设置:")
        editor_frame.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(0, ems_to_pixels(1)))

        # 字体大小
        font_size_label = tk.Label(editor_frame, text="字体大小:")
        font_size_label.pack(anchor="w", padx=ems_to_pixels(1))

        self.font_size_var = tk.StringVar(
            value=str(get_workbench().get_option("view.font_size", 10))
        )
        font_size_combo = ttk.Combobox(
            editor_frame,
            textvariable=self.font_size_var,
            values=["8", "9", "10", "11", "12", "14", "16"],
            state="readonly",
            width=8,
        )
        font_size_combo.pack(anchor="w", padx=ems_to_pixels(2), pady=(ems_to_pixels(0.2), 0))

        # 行号显示
        self.line_numbers_var = tk.BooleanVar(
            value=get_workbench().get_option("view.line_numbers", True)
        )
        line_numbers_check = ttk.Checkbutton(
            editor_frame, text="显示行号", variable=self.line_numbers_var
        )
        line_numbers_check.pack(anchor="w", padx=ems_to_pixels(1), pady=(ems_to_pixels(0.5), 0))

    def _create_section_label(self, text):
        """创建分区标题"""
        return tk.Label(
            self,
            text=text,
            background=self._get_background(),
            foreground="#2C3E50",
            font="Segoe UI 11 bold",
        )

    def _create_option_frame(self, title):
        """创建选项框架"""
        frame = tk.Frame(self, background=self._get_background())

        if title:
            title_label = tk.Label(
                frame,
                text=title,
                background=self._get_background(),
                foreground="#2C3E50",
                font="Segoe UI 9",
            )
            title_label.pack(
                anchor="w", padx=ems_to_pixels(1), pady=(ems_to_pixels(0.5), ems_to_pixels(0.3))
            )

        return frame

    def _get_background(self):
        """获取背景颜色"""
        return "#F8F9FA"

    def _toggle_beginner_theme(self):
        """切换初学者主题"""
        if self.beginner_theme_var.get():
            get_workbench().set_option("ui.theme", "beginner")
        else:
            get_workbench().set_option("ui.theme", "")

    def apply(self, changed_options: List[str]) -> bool:
        """应用配置更改"""
        # 应用主题设置
        if self.beginner_theme_var.get():
            get_workbench().set_option("ui.theme", "beginner")
        else:
            get_workbench().set_option("ui.theme", "")

        # 应用AI助手设置
        get_workbench().set_option("assistance.auto_open_ai", self.auto_open_ai_var.get())

        # 应用编辑器设置
        try:
            font_size = int(self.font_size_var.get())
            get_workbench().set_option("view.font_size", font_size)
        except ValueError:
            pass

        get_workbench().set_option("view.line_numbers", self.line_numbers_var.get())

        return True


def load_plugin():
    """加载插件"""
    # 设置默认配置
    get_workbench().set_default("ui.theme", "beginner")
    get_workbench().set_default("assistance.auto_open_ai", True)
    get_workbench().set_default("view.font_size", 10)
    get_workbench().set_default("view.line_numbers", True)

    # 添加配置页面
    get_workbench().add_configuration_page("beginner", "初学者设置", BeginnerConfigPage, 10)
