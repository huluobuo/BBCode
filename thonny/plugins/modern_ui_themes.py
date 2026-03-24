"""
Modern UI Themes for BBCode
Provides modern light and dark themes with smooth animations
"""

from typing import Optional

from thonny import get_workbench
from thonny.misc_utils import running_on_windows
from thonny.ui_utils import scale
from thonny.workbench import UiThemeSettings


def modern_theme(
    is_dark: bool = False,
) -> UiThemeSettings:
    """
    Modern theme with smooth aesthetics
    """
    if is_dark:
        # Dark mode colors - Modern dark theme
        bg_primary = "#1a1a2e"  # Deep dark blue-purple
        bg_secondary = "#16213e"  # Slightly lighter
        bg_tertiary = "#0f3460"  # Accent dark blue
        bg_card = "#252542"  # Card background

        text_primary = "#eaeaea"  # Primary text
        text_secondary = "#a0a0a0"  # Secondary text
        text_disabled = "#666666"  # Disabled text

        accent_primary = "#e94560"  # Vibrant pink-red accent
        accent_secondary = "#533483"  # Purple accent
        accent_success = "#4ecca3"  # Teal success
        accent_warning = "#f9a825"  # Yellow warning

        border_color = "#2d2d4a"
        hover_bg = "#2a2a4a"
        selected_bg = "#e94560"
    else:
        # Light mode colors - Modern light theme
        bg_primary = "#fafafa"  # Off-white
        bg_secondary = "#ffffff"  # Pure white
        bg_tertiary = "#f0f0f5"  # Light gray
        bg_card = "#ffffff"  # Card background

        text_primary = "#2d3436"  # Dark gray
        text_secondary = "#636e72"  # Medium gray
        text_disabled = "#b2bec3"  # Light gray

        accent_primary = "#6c5ce7"  # Purple accent
        accent_secondary = "#00b894"  # Teal accent
        accent_success = "#00b894"  # Teal success
        accent_warning = "#fdcb6e"  # Yellow warning

        border_color = "#dfe6e9"
        hover_bg = "#f5f6fa"
        selected_bg = "#6c5ce7"

    return {
        ".": {
            "configure": {
                "foreground": text_primary,
                "background": bg_primary,
                "lightcolor": bg_primary,
                "darkcolor": bg_primary,
                "bordercolor": border_color,
                "selectbackground": selected_bg,
                "selectforeground": "#ffffff" if is_dark else "#ffffff",
                "font": "TkDefaultFont",
            },
            "map": {
                "foreground": [("disabled", text_disabled), ("active", text_primary)],
                "background": [("disabled", bg_primary), ("active", hover_bg)],
                "selectbackground": [("!focus", bg_tertiary)],
                "selectforeground": [("!focus", text_primary)],
            },
        },
        "TNotebook": {
            "configure": {
                "bordercolor": border_color,
                "tabmargins": [scale(1), 0, 0, 0],
                "padding": [0, 0, 0, 0],
            }
        },
        "ButtonNotebook.TNotebook": {"configure": {"bordercolor": bg_primary}},
        "ViewNotebook.TNotebook": {"configure": {"bordercolor": bg_primary}},
        "TNotebook.Tab": {
            "configure": {
                "background": bg_primary,
                "bordercolor": border_color,
                "padding": [scale(10), scale(5)],
            },
            "map": {
                "background": [
                    ("selected", bg_secondary),
                    ("!selected", "!active", bg_primary),
                    ("active", "!selected", hover_bg),
                ],
                "bordercolor": [("selected", bg_primary), ("!selected", border_color)],
                "lightcolor": [("selected", bg_secondary), ("!selected", bg_primary)],
            },
        },
        "CustomNotebook": {
            "configure": {
                "bordercolor": border_color,
            }
        },
        "CustomNotebook.Tab": {
            "configure": {
                "background": bg_primary,
                "activebackground": bg_secondary,
                "hoverbackground": hover_bg,
                "indicatorbackground": accent_primary,
                "dynamic_border": 1,
            }
        },
        "TextPanedWindow": {"configure": {"background": bg_secondary}},
        "Treeview": {
            "configure": {
                "background": bg_secondary,
                "borderwidth": 0,
                "relief": "flat",
                "rowheight": scale(22),
            },
            "map": {
                "background": [
                    ("selected", "focus", accent_primary),
                    ("selected", "!focus", bg_tertiary),
                ],
                "foreground": [
                    ("selected", "focus", "#ffffff"),
                    ("selected", "!focus", text_primary),
                ],
            },
        },
        "Heading": {
            "configure": {
                "background": bg_tertiary,
                "lightcolor": bg_tertiary,
                "darkcolor": bg_tertiary,
                "borderwidth": 0,
                "topmost_pixels_to_hide": 0,
                "font": "BoldTkDefaultFont",
            },
            "map": {
                "background": [
                    ("!active", bg_tertiary),
                    ("active", hover_bg),
                ]
            },
        },
        "TEntry": {
            "configure": {
                "fieldbackground": bg_secondary,
                "lightcolor": bg_secondary,
                "insertcolor": text_primary,
                "borderwidth": 1,
                "relief": "solid",
            },
            "map": {
                "background": [("readonly", bg_secondary)],
                "bordercolor": [("focus", accent_primary), ("!focus", border_color)],
                "lightcolor": [("focus", accent_primary)],
            },
        },
        "TCombobox": {
            "configure": {
                "background": bg_secondary,
                "fieldbackground": bg_secondary,
                "selectbackground": bg_secondary,
                "lightcolor": bg_secondary,
                "darkcolor": bg_secondary,
                "bordercolor": border_color,
                "arrowcolor": text_primary,
                "foreground": text_primary,
                "selectforeground": text_primary,
            },
            "map": {
                "background": [("active", bg_primary), ("readonly", bg_primary)],
                "bordercolor": [("focus", accent_primary), ("!focus", border_color)],
            },
        },
        "TScrollbar": {
            "configure": {
                "gripcount": 0,
                "borderwidth": 0,
                "padding": scale(2),
                "relief": "flat",
                "background": bg_tertiary if is_dark else "#c0c0c0",
                "darkcolor": bg_primary,
                "lightcolor": bg_primary,
                "bordercolor": bg_primary,
                "troughcolor": bg_primary,
                "arrowsize": scale(7),
                "width": scale(12),
            },
            "map": {
                "background": [
                    ("!disabled", bg_tertiary if is_dark else "#a0a0a0"),
                    ("disabled", bg_primary),
                ],
            },
        },
        "Vertical.TScrollbar": {
            "layout": [
                (
                    "Vertical.Scrollbar.trough",
                    {
                        "sticky": "ns",
                        "children": [
                            (
                                "Vertical.Scrollbar.padding",
                                {
                                    "sticky": "nswe",
                                    "children": [
                                        (
                                            "Vertical.Scrollbar.thumb",
                                            {"expand": 1, "sticky": "nswe"},
                                        )
                                    ],
                                },
                            ),
                        ],
                    },
                )
            ]
        },
        "Horizontal.TScrollbar": {
            "layout": [
                (
                    "Horizontal.Scrollbar.trough",
                    {
                        "sticky": "we",
                        "children": [
                            (
                                "Horizontal.Scrollbar.padding",
                                {
                                    "sticky": "nswe",
                                    "children": [
                                        (
                                            "Horizontal.Scrollbar.thumb",
                                            {"expand": 1, "sticky": "nswe"},
                                        )
                                    ],
                                },
                            ),
                        ],
                    },
                )
            ],
            "map": {
                "background": [("disabled", bg_primary), ("!disabled", bg_tertiary)],
                "troughcolor": [("disabled", bg_primary)],
                "bordercolor": [("disabled", bg_primary)],
            },
        },
        "TButton": {
            "configure": {
                "background": accent_primary,
                "foreground": "#ffffff",
                "lightcolor": accent_primary,
                "darkcolor": accent_primary,
                "borderwidth": 0,
                "relief": "flat",
                "padding": [scale(15), scale(8)],
                "font": "BoldTkDefaultFont",
            },
            "map": {
                "foreground": [("disabled", text_disabled)],
                "background": [
                    ("pressed", accent_secondary),
                    ("active", accent_secondary),
                ],
                "lightcolor": [
                    ("pressed", accent_secondary),
                    ("active", accent_secondary),
                ],
                "darkcolor": [
                    ("pressed", accent_secondary),
                    ("active", accent_secondary),
                ],
            },
        },
        "TCheckbutton": {
            "configure": {
                "indicatorforeground": text_primary,
                "indicatorbackground": bg_secondary,
            },
            "map": {
                "indicatorforeground": [
                    ("disabled", "alternate", text_disabled),
                    ("disabled", text_disabled),
                ],
                "indicatorbackground": [
                    ("disabled", "alternate", bg_secondary),
                    ("disabled", bg_secondary),
                ],
            },
        },
        "TRadiobutton": {
            "configure": {
                "indicatorforeground": text_primary,
                "indicatorbackground": bg_secondary,
            },
            "map": {
                "indicatorforeground": [
                    ("disabled", "alternate", text_disabled),
                    ("disabled", text_disabled),
                ]
            },
        },
        "Toolbutton": {
            "configure": {"background": bg_primary},
            "map": {"background": [("disabled", bg_primary), ("active", hover_bg)]},
        },
        "CustomToolbutton": {
            "configure": {
                "background": bg_primary,
                "activebackground": hover_bg,
                "foreground": text_primary,
            }
        },
        "TLabel": {"configure": {"foreground": text_primary}},
        "Url.TLabel": {"configure": {"foreground": accent_primary}},
        "Tip.TLabel": {"configure": {"foreground": text_primary, "background": bg_tertiary}},
        "Tip.TFrame": {"configure": {"background": bg_tertiary}},
        "TScale": {
            "configure": {
                "background": accent_primary,
                "troughcolor": bg_tertiary,
                "lightcolor": accent_primary,
                "darkcolor": accent_primary,
                "gripcount": 0,
            },
        },
        "ViewBody.TFrame": {"configure": {"background": bg_secondary}},
        "ViewToolbar.TFrame": {"configure": {"background": bg_tertiary}},
        "ViewToolbar.Toolbutton": {"configure": {"background": bg_tertiary}},
        "ViewTab.TLabel": {"configure": {"background": bg_tertiary, "padding": [scale(8), 0]}},
        "ViewToolbar.TLabel": {
            "configure": {
                "background": bg_tertiary,
                "lightcolor": bg_tertiary,
                "darkcolor": bg_tertiary,
                "bordercolor": bg_tertiary,
                "borderwidth": 0,
                "padding": [scale(8), 0],
            }
        },
        "Active.ViewTab.TLabel": {
            "configure": {
                "foreground": text_primary,
                "background": bg_secondary,
                "lightcolor": bg_secondary,
                "darkcolor": bg_secondary,
                "relief": "flat",
                "bordercolor": accent_primary,
                "borderwidth": 0,
            },
            "map": {
                "lightcolor": [("hover", bg_secondary)],
                "bordercolor": [("hover", accent_primary)],
                "background": [("hover", bg_secondary)],
                "darkcolor": [("hover", bg_secondary)],
            },
        },
        "Inactive.ViewTab.TLabel": {
            "configure": {"foreground": text_secondary},
            "map": {"background": [("hover", hover_bg)]},
        },
        "Text": {
            "configure": {
                "background": bg_secondary,
                "foreground": text_primary,
                "insertbackground": accent_primary,
                "selectbackground": accent_primary,
                "selectforeground": "#ffffff",
            }
        },
        "Gutter": {
            "configure": {
                "background": bg_tertiary if is_dark else bg_primary,
                "foreground": text_secondary,
            }
        },
        "Listbox": {
            "configure": {
                "background": bg_secondary,
                "foreground": text_primary,
                "selectbackground": accent_primary,
                "selectforeground": "#ffffff",
                "disabledforeground": text_disabled,
                "highlightbackground": border_color,
                "highlightcolor": accent_primary,
                "highlightthickness": 0,
                "borderwidth": 0,
            }
        },
        "Menubar": {
            "configure": {
                "custom": running_on_windows(),
                "background": bg_primary,
                "foreground": text_primary,
                "activebackground": accent_primary,
                "activeforeground": "#ffffff",
                "relief": "flat",
            }
        },
        "Menu": {
            "configure": {
                "background": bg_secondary,
                "foreground": text_primary,
                "selectcolor": text_primary,
                "activebackground": accent_primary,
                "activeforeground": "#ffffff",
                "relief": "flat",
                "borderwidth": 1,
            }
        },
        "CustomMenubarLabel.TLabel": {
            "configure": {"padding": [scale(12), scale(4), 0, scale(12)]}
        },
        "TFrame": {"configure": {"background": bg_primary}},
        "TProgressbar": {
            "configure": {
                "background": accent_primary,
                "troughcolor": bg_tertiary,
            }
        },
    }


def load_plugin() -> None:
    """Load modern themes"""
    dark_images = {"tab-close-active": "tab-close-active-dark"}

    # Modern Light Theme
    get_workbench().add_ui_theme(
        "Modern Light",
        "Enhanced Clam",
        lambda: modern_theme(is_dark=False),
    )

    # Modern Dark Theme
    get_workbench().add_ui_theme(
        "Modern Dark",
        "Enhanced Clam",
        lambda: modern_theme(is_dark=True),
        images=dark_images,
    )
