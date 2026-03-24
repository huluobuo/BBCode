"""
Startup Animation for BBCode
Shows a beautiful splash screen with animation during startup
"""

import math
import threading
import tkinter as tk
from tkinter import ttk
from typing import Optional

from thonny import get_workbench


class StartupSplash(tk.Toplevel):
    """Animated startup splash screen"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Window setup
        self.overrideredirect(True)  # No window decorations
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.0)  # Start invisible

        # Size and position
        self.width = 500
        self.height = 350
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        self.x = (self.screen_width - self.width) // 2
        self.y = (self.screen_height - self.height) // 2
        self.geometry(f"{self.width}x{self.height}+{self.x}+{self.y}")

        # Colors based on theme preference
        self.is_dark = self._detect_dark_mode()

        if self.is_dark:
            self.bg_color = "#1a1a2e"
            self.accent_color = "#e94560"
            self.text_color = "#eaeaea"
            self.subtext_color = "#a0a0a0"
        else:
            self.bg_color = "#fafafa"
            self.accent_color = "#6c5ce7"
            self.text_color = "#2d3436"
            self.subtext_color = "#636e72"

        # Canvas for drawing
        self.canvas = tk.Canvas(
            self, width=self.width, height=self.height, bg=self.bg_color, highlightthickness=0
        )
        self.canvas.pack()

        # Animation state
        self.animation_frame = 0
        self.loading_progress = 0
        self.particles = []
        self._closing = False

        # Draw static elements
        self._draw_logo()
        self._draw_text()
        self._draw_progress_bar()
        self._create_particles()

        # Start animations
        self._animate_fade_in()
        self._animate_particles()
        self._animate_loading()

    def _detect_dark_mode(self) -> bool:
        """Detect if system prefers dark mode"""
        try:
            import winreg

            registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key = winreg.OpenKey(
                registry, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            )
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return value == 0
        except:
            # Default to dark mode
            return True

    def _draw_logo(self):
        """Draw the BBCode logo"""
        center_x = self.width // 2
        center_y = 120

        # Draw hexagon shape for logo
        size = 50
        points = []
        for i in range(6):
            angle = math.pi / 3 * i - math.pi / 6
            x = center_x + size * math.cos(angle)
            y = center_y + size * math.sin(angle)
            points.extend([x, y])

        # Hexagon outline
        self.canvas.create_polygon(points, outline=self.accent_color, fill="", width=3, tags="logo")

        # Inner design - code brackets
        self.canvas.create_text(
            center_x,
            center_y,
            text="{ }",
            font=("Consolas", 24, "bold"),
            fill=self.accent_color,
            tags="logo",
        )

        # Animated ring (will be updated)
        self.ring_id = self.canvas.create_oval(
            center_x - size - 10,
            center_y - size - 10,
            center_x + size + 10,
            center_y + size + 10,
            outline=self.accent_color,
            width=2,
            tags="ring",
        )

    def _draw_text(self):
        """Draw application name and subtitle"""
        center_x = self.width // 2

        # Main title
        self.canvas.create_text(
            center_x,
            200,
            text="BBCode",
            font=("Segoe UI", 32, "bold"),
            fill=self.text_color,
            tags="title",
        )

        # Subtitle
        self.canvas.create_text(
            center_x,
            245,
            text="基于 Thonny 的 Python IDE",
            font=("Microsoft YaHei UI", 12),
            fill=self.subtext_color,
            tags="subtitle",
        )

        # Version info
        self.canvas.create_text(
            center_x,
            270,
            text="v1.0.0",
            font=("Consolas", 10),
            fill=self.subtext_color,
            tags="version",
        )

    def _draw_progress_bar(self):
        """Draw loading progress bar"""
        bar_width = 300
        bar_height = 4
        center_x = self.width // 2
        bar_y = 310

        # Background bar
        self.canvas.create_rectangle(
            center_x - bar_width // 2,
            bar_y,
            center_x + bar_width // 2,
            bar_y + bar_height,
            fill=self.subtext_color if self.is_dark else "#e0e0e0",
            outline="",
            tags="progress_bg",
        )

        # Progress fill
        self.progress_fill = self.canvas.create_rectangle(
            center_x - bar_width // 2,
            bar_y,
            center_x - bar_width // 2,
            bar_y + bar_height,
            fill=self.accent_color,
            outline="",
            tags="progress_fill",
        )

        # Loading text
        self.loading_text = self.canvas.create_text(
            center_x,
            bar_y + 20,
            text="正在启动...",
            font=("Microsoft YaHei UI", 9),
            fill=self.subtext_color,
            tags="loading_text",
        )

    def _create_particles(self):
        """Create floating particles"""
        import random

        for _ in range(20):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            size = random.randint(2, 5)
            speed = random.uniform(0.5, 2)

            particle = self.canvas.create_oval(
                x, y, x + size, y + size, fill=self.accent_color, outline="", alpha=0.3
            )

            self.particles.append(
                {
                    "id": particle,
                    "x": x,
                    "y": y,
                    "size": size,
                    "speed": speed,
                    "offset": random.uniform(0, math.pi * 2),
                }
            )

    def _animate_fade_in(self):
        """Fade in the splash screen"""
        alpha = 0.0

        def fade_step():
            nonlocal alpha
            if alpha < 1.0 and not self._closing:
                alpha += 0.05
                self.attributes("-alpha", min(alpha, 1.0))
                self.after(20, fade_step)

        fade_step()

    def _animate_particles(self):
        """Animate floating particles"""
        if self._closing:
            return

        for particle in self.particles:
            # Update position
            particle["y"] -= particle["speed"]
            particle["x"] += math.sin(self.animation_frame * 0.05 + particle["offset"]) * 0.5

            # Reset if out of bounds
            if particle["y"] < -10:
                import random

                particle["y"] = self.height + 10
                particle["x"] = random.randint(0, self.width)

            # Update canvas position
            self.canvas.coords(
                particle["id"],
                particle["x"],
                particle["y"],
                particle["x"] + particle["size"],
                particle["y"] + particle["size"],
            )

        # Animate ring rotation
        center_x = self.width // 2
        center_y = 120
        size = 60
        angle_offset = self.animation_frame * 0.02

        points = []
        for i in range(6):
            angle = math.pi / 3 * i - math.pi / 6 + angle_offset
            x = center_x + size * math.cos(angle)
            y = center_y + size * math.sin(angle)
            points.extend([x, y])

        self.canvas.coords(self.ring_id, *points)

        self.animation_frame += 1
        self.after(30, self._animate_particles)

    def _animate_loading(self):
        """Animate loading progress"""
        if self._closing:
            return

        if self.loading_progress < 100:
            self.loading_progress += random.uniform(0.5, 2)
            self.loading_progress = min(self.loading_progress, 100)

            # Update progress bar
            bar_width = 300
            center_x = self.width // 2
            bar_y = 310
            fill_width = (self.loading_progress / 100) * bar_width

            self.canvas.coords(
                self.progress_fill,
                center_x - bar_width // 2,
                bar_y,
                center_x - bar_width // 2 + fill_width,
                bar_y + 4,
            )

            # Update loading text
            stages = ["正在启动...", "正在加载组件...", "正在初始化...", "即将完成..."]
            stage = min(int(self.loading_progress / 25), len(stages) - 1)
            self.canvas.itemconfig(self.loading_text, text=stages[stage])

            self.after(50, self._animate_loading)

    def set_progress(self, progress: float, text: str = ""):
        """Set loading progress (0-100)"""
        self.loading_progress = progress
        if text:
            self.canvas.itemconfig(self.loading_text, text=text)

    def close(self, callback: Optional[callable] = None):
        """Close splash screen with fade out"""
        self._closing = True
        alpha = 1.0

        def fade_out():
            nonlocal alpha
            if alpha > 0:
                alpha -= 0.08
                self.attributes("-alpha", max(alpha, 0))
                self.after(20, fade_out)
            else:
                self.destroy()
                if callback:
                    callback()

        fade_out()


_splash_instance: Optional[StartupSplash] = None


def show_splash() -> StartupSplash:
    """Show the startup splash screen"""
    global _splash_instance

    # Create hidden root window if needed
    root = tk.Tk()
    root.withdraw()

    _splash_instance = StartupSplash(root)
    return _splash_instance


def close_splash(callback: Optional[callable] = None):
    """Close the splash screen"""
    global _splash_instance

    if _splash_instance:
        _splash_instance.close(callback)
        _splash_instance = None


def load_plugin() -> None:
    """Load startup animation plugin"""
    # Plugin is loaded automatically when needed
    pass
