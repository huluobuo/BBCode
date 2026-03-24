"""
Theme Switcher for BBCode
Provides quick theme switching between light and dark modes
"""

import tkinter as tk
from tkinter import ttk

from thonny import get_workbench
from thonny.languages import tr


class ThemeSwitcher:
    """Manages theme switching functionality"""

    def __init__(self):
        self.workbench = get_workbench()
        self._current_theme_mode = self._detect_initial_mode()

    def _detect_initial_mode(self) -> str:
        """Detect initial theme mode from current theme"""
        current_theme = self.workbench.get_option("view.ui_theme", "")
        if "dark" in current_theme.lower() or "Dark" in current_theme:
            return "dark"
        return "light"

    def toggle_theme(self):
        """Toggle between light and dark themes"""
        if self._current_theme_mode == "light":
            self.set_dark_theme()
        else:
            self.set_light_theme()

    def set_light_theme(self):
        """Set light theme"""
        self._current_theme_mode = "light"
        self.workbench.set_option("view.ui_theme", "Modern Light")
        self.workbench.set_option("view.syntax_theme", "Default Light")
        self._apply_theme()

    def set_dark_theme(self):
        """Set dark theme"""
        self._current_theme_mode = "dark"
        self.workbench.set_option("view.ui_theme", "Modern Dark")
        self.workbench.set_option("view.syntax_theme", "Default Dark")
        self._apply_theme()

    def _apply_theme(self):
        """Apply the selected theme"""
        self.workbench.reload_themes()
        self.workbench.update_fonts()

        # Update editor notebook appearance
        if hasattr(self.workbench, "_editor_notebook"):
            self.workbench._editor_notebook.update_appearance()

        # Generate theme changed event
        self.workbench.event_generate("ThemeChanged")

    def get_current_mode(self) -> str:
        """Get current theme mode"""
        return self._current_theme_mode


class ThemeSwitcherButton(ttk.Frame):
    """Theme switcher toggle button with icon"""

    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)

        self.switcher = ThemeSwitcher()

        # Create button
        self.button = ttk.Button(
            self, text="🌙", command=self._on_click, width=3  # Moon icon for dark mode
        )
        self.button.pack()

        self._update_icon()

    def _on_click(self):
        """Handle button click"""
        self.switcher.toggle_theme()
        self._update_icon()

    def _update_icon(self):
        """Update button icon based on current mode"""
        if self.switcher.get_current_mode() == "dark":
            self.button.configure(text="☀️")  # Sun icon for light mode
        else:
            self.button.configure(text="🌙")  # Moon icon for dark mode


def load_plugin() -> None:
    """Load theme switcher plugin"""
    workbench = get_workbench()

    # Create theme switcher instance
    workbench._theme_switcher = ThemeSwitcher()

    # Add toggle theme command
    workbench.add_command(
        "toggle_theme",
        "view",
        "切换主题 (亮/暗)",
        lambda: workbench._theme_switcher.toggle_theme(),
        default_sequence="<Control-Shift-T>",
        group=60,
    )

    # Add theme submenu
    workbench.add_command(
        "set_light_theme",
        "view",
        "亮色主题",
        lambda: workbench._theme_switcher.set_light_theme(),
        group=60,
    )

    workbench.add_command(
        "set_dark_theme",
        "view",
        "暗色主题",
        lambda: workbench._theme_switcher.set_dark_theme(),
        group=60,
    )

    # Set default theme if not set
    if not workbench.get_option("view.ui_theme"):
        # Detect system preference
        try:
            import winreg

            registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key = winreg.OpenKey(
                registry, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            )
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            if value == 0:
                workbench.set_option("view.ui_theme", "Modern Dark")
                workbench.set_option("view.syntax_theme", "Default Dark")
            else:
                workbench.set_option("view.ui_theme", "Modern Light")
                workbench.set_option("view.syntax_theme", "Default Light")
        except:
            # Default to modern light
            workbench.set_option("view.ui_theme", "Modern Light")
            workbench.set_option("view.syntax_theme", "Default Light")
