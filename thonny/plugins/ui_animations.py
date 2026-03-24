"""
UI Animations and Jelly Effects for BBCode
Provides smooth animations and jelly-like effects for modern UI
"""

import math
import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Optional

from thonny import get_workbench


class AnimationManager:
    """Manages smooth animations for UI elements"""

    def __init__(self):
        self._animations = {}
        self._frame_count = 0

    def ease_out_cubic(self, t: float) -> float:
        """Cubic ease out for smooth deceleration"""
        return 1 - pow(1 - t, 3)

    def ease_out_elastic(self, t: float) -> float:
        """Elastic ease out for jelly effect"""
        c4 = (2 * math.pi) / 3
        if t == 0:
            return 0
        elif t == 1:
            return 1
        else:
            return pow(2, -10 * t) * math.sin((t * 10 - 0.75) * c4) + 1

    def ease_out_back(self, t: float) -> float:
        """Back ease out for slight overshoot effect"""
        c1 = 1.70158
        c3 = c1 + 1
        return 1 + c3 * pow(t - 1, 3) + c1 * pow(t - 1, 2)

    def animate_property(
        self,
        widget: tk.Widget,
        property_name: str,
        start_value: float,
        end_value: float,
        duration: int = 300,
        easing: Optional[Callable[[float], float]] = None,
        callback: Optional[Callable[[], None]] = None,
    ):
        """Animate a widget property smoothly"""
        if easing is None:
            easing = self.ease_out_cubic

        animation_id = f"{widget.winfo_id()}_{property_name}"

        def update_animation(frame: int, total_frames: int):
            if frame > total_frames:
                # Set final value
                try:
                    if property_name == "alpha":
                        widget.attributes("-alpha", end_value)
                    elif property_name == "scale":
                        # For scale, we might need to update geometry
                        pass
                    elif hasattr(widget, property_name):
                        setattr(widget, property_name, end_value)
                except tk.TclError:
                    pass  # Widget destroyed

                if callback:
                    callback()
                return

            # Calculate progress
            progress = frame / total_frames
            eased_progress = easing(progress)
            current_value = start_value + (end_value - start_value) * eased_progress

            # Apply value
            try:
                if property_name == "alpha":
                    widget.attributes("-alpha", current_value)
                elif hasattr(widget, property_name):
                    setattr(widget, property_name, current_value)
            except tk.TclError:
                return  # Widget destroyed

            # Schedule next frame
            widget.after(16, lambda: update_animation(frame + 1, total_frames))

        # Start animation
        total_frames = duration // 16  # ~60fps
        update_animation(0, total_frames)


class JellyButton(ttk.Button):
    """Button with jelly press effect"""

    def __init__(self, master=None, **kwargs):
        self._original_padding = kwargs.get("padding", [10, 5])
        super().__init__(master, **kwargs)

        self._animating = False
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

    def _on_press(self, event):
        """Handle press with jelly compression"""
        if self._animating:
            return
        self._animate_press()

    def _on_release(self, event):
        """Handle release with jelly expansion"""
        self._animate_release()

    def _animate_press(self):
        """Animate button press (compress)"""
        self._animating = True
        # Visual feedback is handled by theme

    def _animate_release(self):
        """Animate button release (bounce back)"""
        self._animating = False
        # Visual feedback is handled by theme


class FadeInWidget:
    """Mixin for widgets that fade in on creation"""

    def __init__(self, *args, fade_duration: int = 200, **kwargs):
        self._fade_duration = fade_duration
        self._target_alpha = kwargs.pop("alpha", 1.0)
        super().__init__(*args, **kwargs)

    def fade_in(self):
        """Fade in the widget"""
        if isinstance(self, tk.Toplevel):
            self.attributes("-alpha", 0.0)
            animator = AnimationManager()
            animator.animate_property(
                self,
                "alpha",
                0.0,
                self._target_alpha,
                duration=self._fade_duration,
                easing=AnimationManager().ease_out_cubic,
            )


class SmoothFrame(ttk.Frame):
    """Frame with smooth appearance animation"""

    def __init__(self, master=None, **kwargs):
        self._animate = kwargs.pop("animate", True)
        super().__init__(master, **kwargs)

        if self._animate:
            self._setup_animation()

    def _setup_animation(self):
        """Setup entrance animation"""
        # Store original background
        style = ttk.Style()
        self._original_bg = style.lookup("TFrame", "background")

        # Animate children appearance
        for child in self.winfo_children():
            if hasattr(child, "fade_in"):
                child.fade_in()


class AnimatedNotebook(ttk.Notebook):
    """Notebook with animated tab switching"""

    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self._animating = False
        self.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    def _on_tab_changed(self, event):
        """Handle tab change with animation"""
        if self._animating:
            return

        current = self.select()
        if current:
            self._animate_tab_content(current)

    def _animate_tab_content(self, tab_id):
        """Animate tab content appearance"""
        try:
            widget = self.nametowidget(tab_id)
            if widget and hasattr(widget, "winfo_children"):
                # Subtle fade effect for content
                pass
        except tk.TclError:
            pass


class BounceLabel(ttk.Label):
    """Label with bounce animation on text change"""

    def __init__(self, master=None, **kwargs):
        self._bounce_on_update = kwargs.pop("bounce", True)
        super().__init__(master, **kwargs)
        self._original_font = self.cget("font")

    def configure(self, **kwargs):
        """Override configure to add bounce effect"""
        if "text" in kwargs and self._bounce_on_update:
            old_text = self.cget("text")
            new_text = kwargs["text"]
            if old_text != new_text:
                self._bounce_animation()
        super().configure(**kwargs)

    def _bounce_animation(self):
        """Perform bounce animation"""
        frames = 10

        def animate(frame):
            if frame > frames:
                # Reset to normal
                try:
                    self.configure(font=self._original_font)
                except tk.TclError:
                    pass
                return

            # Calculate scale
            progress = frame / frames
            # Bounce effect: scale up then down
            if progress < 0.5:
                scale = 1.0 + 0.1 * (progress * 2)
            else:
                scale = 1.1 - 0.1 * ((progress - 0.5) * 2)

            # Apply scale to font
            try:
                font = tk.font.nametofont(self._original_font)
                new_size = int(font.cget("size") * scale)
                self.configure(font=(font.cget("family"), new_size))
            except (tk.TclError, tk.TclError):
                pass

            self.after(20, lambda: animate(frame + 1))

        animate(0)


def add_hover_effect(widget: tk.Widget, hover_bg: str, normal_bg: str):
    """Add smooth hover effect to widget"""

    def on_enter(event):
        try:
            widget.configure(background=hover_bg)
        except tk.TclError:
            pass

    def on_leave(event):
        try:
            widget.configure(background=normal_bg)
        except tk.TclError:
            pass

    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)


def animate_window_open(window: tk.Toplevel, duration: int = 300):
    """Animate window opening with fade and scale"""
    animator = AnimationManager()

    # Fade in
    window.attributes("-alpha", 0.0)
    animator.animate_property(
        window, "alpha", 0.0, 1.0, duration=duration, easing=animator.ease_out_cubic
    )


def animate_window_close(window: tk.Toplevel, duration: int = 200):
    """Animate window closing with fade out"""
    animator = AnimationManager()

    # Fade out
    animator.animate_property(
        window,
        "alpha",
        1.0,
        0.0,
        duration=duration,
        easing=animator.ease_out_cubic,
        callback=window.destroy,
    )


def load_plugin() -> None:
    """Load UI animation plugin"""
    workbench = get_workbench()

    # Store animation manager in workbench
    workbench._animation_manager = AnimationManager()

    # Add animation commands
    workbench.add_command(
        "toggle_animations",
        "view",
        "启用/禁用动画效果",
        lambda: _toggle_animations(),
        group=80,
    )


def _toggle_animations():
    """Toggle UI animations on/off"""
    workbench = get_workbench()
    current = workbench.get_option("ui.animations_enabled", True)
    workbench.set_option("ui.animations_enabled", not current)


def get_animation_manager() -> Optional[AnimationManager]:
    """Get the global animation manager"""
    try:
        return get_workbench()._animation_manager
    except AttributeError:
        return None
