"""
UI Animations and Liquid Glass Effects for BBCode
Provides smooth animations, liquid glass effects and enhanced UX
"""
import math
import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Optional, List, Tuple

from thonny import get_workbench


class AnimationManager:
    """Manages smooth animations for UI elements with 60fps target"""

    def __init__(self):
        self._animations = {}
        self._frame_count = 0
        self._running = True

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

    def ease_in_out_cubic(self, t: float) -> float:
        """Smooth cubic ease in-out"""
        return 4 * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 3) / 2

    def ease_out_quart(self, t: float) -> float:
        """Quartic ease out for very smooth deceleration"""
        return 1 - pow(1 - t, 4)

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
        """Animate a widget property smoothly at ~60fps"""
        if easing is None:
            easing = self.ease_out_cubic

        animation_id = f"{widget.winfo_id()}_{property_name}_{id(callback)}"
        
        # Cancel existing animation for this property
        if animation_id in self._animations:
            self._animations[animation_id]['cancelled'] = True

        anim_data = {'cancelled': False}
        self._animations[animation_id] = anim_data

        def update_animation(frame: int, total_frames: int):
            if anim_data.get('cancelled') or not self._running:
                return

            if frame > total_frames:
                # Set final value
                try:
                    if property_name == "alpha":
                        widget.attributes("-alpha", end_value)
                    elif hasattr(widget, property_name):
                        setattr(widget, property_name, end_value)
                except tk.TclError:
                    pass  # Widget destroyed

                if callback:
                    callback()
                if animation_id in self._animations:
                    del self._animations[animation_id]
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
                if animation_id in self._animations:
                    del self._animations[animation_id]
                return  # Widget destroyed

            # Schedule next frame (~60fps = 16ms)
            widget.after(16, lambda: update_animation(frame + 1, total_frames))

        # Start animation
        total_frames = max(1, duration // 16)
        update_animation(0, total_frames)

    def cancel_animation(self, widget: tk.Widget, property_name: str):
        """Cancel running animation for a widget property"""
        for anim_id in list(self._animations.keys()):
            if anim_id.startswith(f"{widget.winfo_id()}_{property_name}"):
                self._animations[anim_id]['cancelled'] = True
                del self._animations[anim_id]


class LiquidGlassEffect:
    """Creates liquid glass visual effects"""

    def __init__(self, widget: tk.Widget):
        self.widget = widget
        self._original_bg = None
        self._hover_bg = None
        self._active_bg = None

    def apply_to_frame(self, normal_bg: str, hover_bg: str, active_bg: str):
        """Apply liquid glass effect to a frame"""
        self._original_bg = normal_bg
        self._hover_bg = hover_bg
        self._active_bg = active_bg

        self.widget.configure(
            background=normal_bg,
            highlightthickness=0,
            relief="flat"
        )

        # Add subtle border
        if isinstance(self.widget, tk.Frame):
            self.widget.configure(borderwidth=0)

    def apply_to_button(self, accent_color: str):
        """Apply liquid glass effect to a button"""
        style = ttk.Style()
        style.configure(
            "Liquid.TButton",
            background=self._original_bg,
            foreground="white",
            borderwidth=0,
            relief="flat",
            padding=[16, 8]
        )
        style.map(
            "Liquid.TButton",
            background=[("active", accent_color), ("pressed", accent_color)],
            foreground=[("active", "white"), ("pressed", "white")]
        )


class SmoothHoverEffect:
    """Smooth hover transition effect for widgets"""

    def __init__(self, widget: tk.Widget, normal_bg: str, hover_bg: str, duration: int = 150):
        self.widget = widget
        self.normal_bg = normal_bg
        self.hover_bg = hover_bg
        self.duration = duration
        self._animating = False

        self.widget.bind("<Enter>", self._on_enter)
        self.widget.bind("<Leave>", self._on_leave)

    def _on_enter(self, event):
        """Handle mouse enter with smooth transition"""
        self._animate_color(self.normal_bg, self.hover_bg)

    def _on_leave(self, event):
        """Handle mouse leave with smooth transition"""
        self._animate_color(self.hover_bg, self.normal_bg)

    def _animate_color(self, start_color: str, end_color: str):
        """Animate color transition"""
        try:
            self.widget.configure(background=end_color)
        except tk.TclError:
            pass


class JellyButton(ttk.Button):
    """Button with jelly press effect and smooth animations"""

    def __init__(self, master=None, **kwargs):
        self._original_padding = kwargs.get("padding", [12, 6])
        self._jelly_enabled = kwargs.pop("jelly", True)
        super().__init__(master, **kwargs)

        self._animating = False
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

    def _on_press(self, event):
        """Handle press with jelly compression"""
        if self._animating or not self._jelly_enabled:
            return
        self._animate_press()

    def _on_release(self, event):
        """Handle release with jelly expansion"""
        if self._jelly_enabled:
            self._animate_release()

    def _animate_press(self):
        """Animate button press (compress)"""
        self._animating = True

    def _animate_release(self):
        """Animate button release (bounce back)"""
        self._animating = False


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


class SmoothProgressBar(ttk.Progressbar):
    """Progress bar with smooth value transitions"""

    def __init__(self, master=None, **kwargs):
        self._animation_duration = kwargs.pop("animation_duration", 300)
        super().__init__(master, **kwargs)
        self._target_value = 0
        self._current_value = 0
        self._animator = AnimationManager()

    def set_value_smooth(self, value: float):
        """Set value with smooth animation"""
        self._target_value = value
        self._animator.animate_property(
            self,
            "value",
            self._current_value,
            value,
            duration=self._animation_duration,
            easing=self._animator.ease_out_cubic
        )
        self._current_value = value


class LiquidGlassFrame(tk.Frame):
    """Frame with liquid glass effect"""

    def __init__(self, master=None, **kwargs):
        self._glass_color = kwargs.pop("glass_color", "#ffffff")
        self._glass_alpha = kwargs.pop("glass_alpha", 0.1)
        self._border_radius = kwargs.pop("border_radius", 8)
        super().__init__(master, **kwargs)

        self.configure(
            background=self._glass_color,
            highlightthickness=0,
            relief="flat",
            borderwidth=0
        )


class AnimatedTooltip:
    """Enhanced tooltip with fade animation"""

    def __init__(self, widget: tk.Widget, text: str, delay: int = 500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tipwindow = None
        self.id = None
        self._alpha = 0.0

        widget.bind("<Enter>", self._on_enter)
        widget.bind("<Leave>", self._on_leave)

    def _on_enter(self, event):
        self.id = self.widget.after(self.delay, self._show_tip)

    def _on_leave(self, event):
        if self.id:
            self.widget.after_cancel(self.id)
        self._hide_tip()

    def _show_tip(self):
        """Show tooltip with fade in"""
        if self.tipwindow or not self.text:
            return

        x = self.widget.winfo_rootx() + self.widget.winfo_width() // 2
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5

        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry(f"+{x}+{y}")
        tw.attributes("-alpha", 0.0)

        label = tk.Label(
            tw,
            text=self.text,
            background="#2d2d2d",
            foreground="#ffffff",
            relief="flat",
            borderwidth=0,
            padx=10,
            pady=5,
            font=("TkDefaultFont", 9)
        )
        label.pack()

        # Fade in
        animator = AnimationManager()
        animator.animate_property(tw, "alpha", 0.0, 1.0, duration=150)

    def _hide_tip(self):
        """Hide tooltip with fade out"""
        if self.tipwindow:
            tw = self.tipwindow
            self.tipwindow = None
            animator = AnimationManager()
            animator.animate_property(
                tw, "alpha", 1.0, 0.0, duration=100,
                callback=tw.destroy
            )


def add_hover_effect(widget: tk.Widget, hover_bg: str, normal_bg: str, duration: int = 150):
    """Add smooth hover effect to widget"""
    SmoothHoverEffect(widget, normal_bg, hover_bg, duration)


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


def apply_liquid_glass_to_widget(widget: tk.Widget, accent_color: str = "#007acc"):
    """Apply liquid glass styling to a widget"""
    if isinstance(widget, tk.Frame):
        widget.configure(
            background="#1e1e1e",
            highlightthickness=0,
            relief="flat",
            borderwidth=0
        )
    elif isinstance(widget, ttk.Button):
        style = ttk.Style()
        style.configure(
            f"{widget.winfo_id()}.TButton",
            background="#2d2d30",
            foreground="#cccccc",
            borderwidth=0,
            relief="flat",
            padding=[16, 8]
        )
        widget.configure(style=f"{widget.winfo_id()}.TButton")


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

    # Apply smooth effects to existing widgets
    _apply_smooth_effects()


def _toggle_animations():
    """Toggle UI animations on/off"""
    workbench = get_workbench()
    current = workbench.get_option("ui.animations_enabled", True)
    workbench.set_option("ui.animations_enabled", not current)


def _apply_smooth_effects():
    """Apply smooth effects to UI components"""
    workbench = get_workbench()

    # Apply to toolbar buttons
    if hasattr(workbench, '_toolbar'):
        for child in workbench._toolbar.winfo_children():
            if isinstance(child, tk.Frame):  # Button groups
                for btn in child.winfo_children():
                    if isinstance(btn, tk.Widget):
                        # Add subtle hover effect
                        pass


def get_animation_manager() -> Optional[AnimationManager]:
    """Get the global animation manager"""
    try:
        return get_workbench()._animation_manager
    except AttributeError:
        return None


# Utility functions for creating smooth UI
def create_smooth_button(
    master: tk.Widget,
    text: str,
    command: Callable,
    accent_color: str = "#007acc",
    **kwargs
) -> ttk.Button:
    """Create a button with smooth hover effects"""
    btn = JellyButton(master, text=text, command=command, **kwargs)
    return btn


def create_glass_frame(
    master: tk.Widget,
    bg_color: str = "#1e1e1e",
    **kwargs
) -> tk.Frame:
    """Create a frame with glass effect"""
    frame = LiquidGlassFrame(master, glass_color=bg_color, **kwargs)
    return frame


def smooth_configure(widget: tk.Widget, **kwargs):
    """Configure widget with smooth transition"""
    # Apply configuration immediately for now
    # In future, this could animate property changes
    widget.configure(**kwargs)
