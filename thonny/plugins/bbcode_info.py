"""
BBCode Info Plugin
Shows BBCode branding and Thonny-based development info in the editor
"""

import tkinter as tk
from tkinter import ttk

from thonny import get_workbench
from thonny.languages import tr


class BBCodeInfoPanel(ttk.Frame):
    """Panel showing BBCode info in editor"""

    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)

        # Configure style
        self.configure(style="InfoPanel.TFrame")

        # Create info label
        self.info_label = ttk.Label(
            self,
            text="🚀 BBCode - 基于 Thonny 的 Python IDE",
            font=("Microsoft YaHei UI", 9),
            foreground=self._get_text_color(),
            background=self._get_bg_color(),
        )
        self.info_label.pack(side=tk.LEFT, padx=10, pady=5)

        # Create version label
        self.version_label = ttk.Label(
            self,
            text="v1.0.0",
            font=("Consolas", 8),
            foreground=self._get_subtext_color(),
            background=self._get_bg_color(),
        )
        self.version_label.pack(side=tk.LEFT, padx=5, pady=5)

        # Create theme toggle button
        self.theme_btn = ttk.Button(self, text="🌙", width=3, command=self._toggle_theme)
        self.theme_btn.pack(side=tk.RIGHT, padx=5, pady=3)

        # Bind theme change event
        get_workbench().bind("ThemeChanged", self._on_theme_changed, True)

    def _get_text_color(self) -> str:
        """Get text color based on theme"""
        workbench = get_workbench()
        if workbench.uses_dark_ui_theme():
            return "#eaeaea"
        return "#2d3436"

    def _get_subtext_color(self) -> str:
        """Get subtext color based on theme"""
        workbench = get_workbench()
        if workbench.uses_dark_ui_theme():
            return "#a0a0a0"
        return "#636e72"

    def _get_bg_color(self) -> str:
        """Get background color based on theme"""
        workbench = get_workbench()
        if workbench.uses_dark_ui_theme():
            return "#1a1a2e"
        return "#fafafa"

    def _on_theme_changed(self, event=None):
        """Handle theme change"""
        self.info_label.configure(
            foreground=self._get_text_color(), background=self._get_bg_color()
        )
        self.version_label.configure(
            foreground=self._get_subtext_color(), background=self._get_bg_color()
        )
        self.configure(style="InfoPanel.TFrame")
        self._update_theme_icon()

    def _toggle_theme(self):
        """Toggle between light and dark themes"""
        try:
            switcher = get_workbench()._theme_switcher
            switcher.toggle_theme()
            self._update_theme_icon()
        except AttributeError:
            pass

    def _update_theme_icon(self):
        """Update theme toggle button icon"""
        try:
            switcher = get_workbench()._theme_switcher
            if switcher.get_current_mode() == "dark":
                self.theme_btn.configure(text="☀️")
            else:
                self.theme_btn.configure(text="🌙")
        except AttributeError:
            pass


class EditorStatusBarAddon:
    """Adds BBCode info to editor status bar"""

    def __init__(self):
        self.workbench = get_workbench()
        self._setup_ui()

    def _setup_ui(self):
        """Setup the UI components"""
        # Get status bar
        try:
            statusbar = self.workbench._statusbar

            # Add BBCode branding label
            self.branding_label = ttk.Label(
                statusbar,
                text="BBCode",
                font=("Segoe UI", 8, "bold"),
                foreground=self._get_accent_color(),
            )
            self.branding_label.grid(row=1, column=0, sticky="w", padx=(10, 5))

            # Add separator
            separator = ttk.Separator(statusbar, orient=tk.VERTICAL)
            separator.grid(row=1, column=1, sticky="ns", padx=5, pady=2)

            # Add Thonny based label
            self.thonny_label = ttk.Label(
                statusbar,
                text="基于 Thonny",
                font=("Microsoft YaHei UI", 8),
                foreground=self._get_text_color(),
            )
            self.thonny_label.grid(row=1, column=2, sticky="w", padx=5)

            # Bind theme change
            self.workbench.bind("ThemeChanged", self._on_theme_changed, True)

        except AttributeError:
            pass

    def _get_accent_color(self) -> str:
        """Get accent color based on theme"""
        if self.workbench.uses_dark_ui_theme():
            return "#e94560"
        return "#6c5ce7"

    def _get_text_color(self) -> str:
        """Get text color based on theme"""
        if self.workbench.uses_dark_ui_theme():
            return "#a0a0a0"
        return "#636e72"

    def _on_theme_changed(self, event=None):
        """Handle theme change"""
        self.branding_label.configure(foreground=self._get_accent_color())
        self.thonny_label.configure(foreground=self._get_text_color())


class WelcomeMessageAddon:
    """Adds welcome message with BBCode branding"""

    def __init__(self):
        self.workbench = get_workbench()
        self._show_welcome()

    def _show_welcome(self):
        """Show welcome message in shell"""
        try:
            shell = self.workbench.get_view("ShellView")
            if shell and hasattr(shell, "text"):
                # Insert welcome message
                welcome_text = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   🚀 BBCode v1.0.0 - 基于 Thonny 的 Python IDE              ║
║                                                              ║
║   快捷键:                                                    ║
║   • Ctrl+Shift+T - 切换主题                                 ║
║   • F1 - 帮助文档                                           ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

"""
                # We can't easily insert to shell, so we'll just log it
                import logging

                logger = logging.getLogger(__name__)
                logger.info("BBCode initialized successfully")
        except Exception:
            pass


def load_plugin() -> None:
    """Load BBCode info plugin"""
    workbench = get_workbench()

    # Add info panel to editor (if possible)
    # Note: This is a simplified version - full integration would require
    # modifying the editor notebook

    # Add status bar addon
    try:
        workbench._bbcode_status_addon = EditorStatusBarAddon()
    except Exception:
        pass

    # Show welcome message
    try:
        workbench._bbcode_welcome = WelcomeMessageAddon()
    except Exception:
        pass

    # Add about BBCode command
    workbench.add_command(
        "about_bbcode",
        "help",
        "关于 BBCode",
        lambda: _show_about_dialog(),
        group=100,
    )


def _show_about_dialog():
    """Show about BBCode dialog"""
    from tkinter import messagebox

    about_text = """BBCode v1.0.0

基于 Thonny 的 Python IDE 二次开发

特性:
• 现代化 UI 设计
• 亮色/暗色主题切换
• 流畅的动画效果
• 基于 Thonny 的强大功能

致谢:
感谢 Thonny 项目的所有贡献者
"""

    messagebox.showinfo("关于 BBCode", about_text)
