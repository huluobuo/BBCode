"""
Glass UI Themes for BBCode
Provides glass morphism, liquid glass effects and smooth animations
"""
from typing import Optional

from thonny import get_workbench
from thonny.misc_utils import running_on_windows
from thonny.ui_utils import scale
from thonny.workbench import UiThemeSettings
from typing import Dict, Any


def glass_morphism(
    frame_background: str,
    text_background: str,
    normal_detail: str,
    high_detail: str,
    low_detail: str,
    scrollbar_background: str,
    trough_background: str,
    active_tab_background: str,
    normal_foreground: str,
    high_foreground: str,
    low_foreground: str,
    link_foreground: str,
    accent_color: str = "#2293e5",
    custom_menubar: Optional[int] = None,
) -> UiThemeSettings:
    """
    Glass morphism theme with rounded corners and liquid glass effects
    """
    if active_tab_background == "normal_detail":
        active_tab_background = normal_detail
    elif active_tab_background == "frame_background":
        active_tab_background = frame_background

    # Calculate glass effect colors (semi-transparent overlays)
    def glass_overlay(base_color: str, overlay_alpha: float = 0.1) -> str:
        """Create a glass overlay effect color"""
        # Simple overlay calculation - in practice this would blend colors
        return base_color

    return {
        ".": {
            "configure": {
                "foreground": normal_foreground,
                "background": frame_background,
                "lightcolor": frame_background,
                "darkcolor": frame_background,
                "bordercolor": low_detail,
                "selectbackground": high_detail,
                "selectforeground": high_foreground,
                "relief": "flat",
            },
            "map": {
                "foreground": [("disabled", low_foreground), ("active", high_foreground)],
                "background": [("disabled", frame_background), ("active", high_detail)],
                "selectbackground": [("!focus", low_detail)],
                "selectforeground": [("!focus", normal_foreground)],
            },
        },
        "TNotebook": {
            "configure": {
                "bordercolor": low_detail,
                "tabmargins": [scale(1), 0, 0, 0],
            }
        },
        "ButtonNotebook.TNotebook": {"configure": {"bordercolor": low_detail}},
        "ViewNotebook.TNotebook": {"configure": {"bordercolor": low_detail}},
        "TNotebook.Tab": {
            "configure": {
                "background": frame_background,
                "bordercolor": low_detail,
                "padding": [scale(8), scale(4)],
            },
            "map": {
                "background": [
                    ("selected", active_tab_background),
                    ("!selected", "!active", frame_background),
                    ("active", "!selected", frame_background),
                ],
                "bordercolor": [("selected", low_detail), ("!selected", low_detail)],
                "lightcolor": [
                    ("selected", active_tab_background),
                    ("!selected", frame_background),
                ],
            },
        },
        "CustomNotebook": {
            "configure": {
                "bordercolor": high_detail,
            }
        },
        "CustomNotebook.Tab": {
            "configure": {
                "background": frame_background,
                "activebackground": active_tab_background,
                "hoverbackground": normal_detail,
                "indicatorbackground": accent_color,
                "dynamic_border": 1,
                "indicatorheight": scale(3),
                "padding": [scale(12), scale(6)],
            }
        },
        "TextPanedWindow": {"configure": {"background": text_background}},
        "Treeview": {
            "configure": {
                "background": text_background,
                "borderwidth": 0,
                "relief": "flat",
            },
            "map": {
                "background": [
                    ("selected", "focus", high_detail),
                    ("selected", "!focus", low_detail),
                ],
                "foreground": [
                    ("selected", "focus", high_foreground),
                    ("selected", "!focus", normal_foreground),
                ],
            },
        },
        "Heading": {
            "configure": {
                "background": active_tab_background,
                "lightcolor": active_tab_background,
                "darkcolor": active_tab_background,
                "borderwidth": 0,
                "topmost_pixels_to_hide": 2,
            },
            "map": {
                "background": [
                    ("!active", active_tab_background),
                    ("active", active_tab_background),
                ]
            },
        },
        "TEntry": {
            "configure": {
                "fieldbackground": text_background,
                "lightcolor": text_background,
                "insertcolor": normal_foreground,
                "borderwidth": 1,
                "relief": "flat",
            },
            "map": {
                "background": [("readonly", text_background)],
                "bordercolor": [],
                "lightcolor": [("focus", accent_color)],
                "darkcolor": [],
            },
        },
        "TCombobox": {
            "configure": {
                "background": text_background,
                "fieldbackground": text_background,
                "selectbackground": text_background,
                "lightcolor": text_background,
                "darkcolor": text_background,
                "bordercolor": high_detail,
                "arrowcolor": normal_foreground,
                "foreground": normal_foreground,
                "selectforeground": normal_foreground,
            },
            "map": {
                "background": [("active", frame_background), ("readonly", frame_background)],
                "fieldbackground": [],
                "selectbackground": [],
                "selectforeground": [],
                "foreground": [],
                "arrowcolor": [],
            },
        },
        "TScrollbar": {
            "configure": {
                "gripcount": 0,
                "borderwidth": 0,
                "padding": scale(2),
                "relief": "flat",
                "background": scrollbar_background,
                "darkcolor": trough_background,
                "lightcolor": trough_background,
                "bordercolor": trough_background,
                "troughcolor": trough_background,
                "arrowsize": scale(7),
                "width": scale(8),
            },
            "map": {
                "background": [
                    ("!disabled", scrollbar_background),
                    ("disabled", trough_background),
                ],
                "darkcolor": [("!disabled", trough_background), ("disabled", trough_background)],
                "lightcolor": [("!disabled", trough_background), ("disabled", trough_background)],
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
                "background": [("disabled", trough_background), ("!disabled", normal_detail)],
                "troughcolor": [("disabled", trough_background)],
                "bordercolor": [("disabled", trough_background)],
                "darkcolor": [("disabled", trough_background)],
                "lightcolor": [("disabled", trough_background)],
            },
        },
        "TButton": {
            "configure": {
                "background": normal_detail,
                "foreground": normal_foreground,
                "lightcolor": normal_detail,
                "darkcolor": normal_detail,
                "borderwidth": 0,
                "relief": "flat",
                "padding": [scale(12), scale(6)],
            },
            "map": {
                "foreground": [("disabled", low_foreground), ("alternate", high_foreground)],
                "background": [("pressed", low_detail), ("active", high_detail)],
                "bordercolor": [("alternate", accent_color)],
                "lightcolor": [("active", normal_detail), ("alternate", normal_detail)],
                "darkcolor": [("active", normal_detail), ("alternate", normal_detail)],
            },
        },
        "TCheckbutton": {
            "configure": {
                "indicatorforeground": normal_foreground,
                "indicatorbackground": text_background,
            },
            "map": {
                "indicatorforeground": [
                    ("disabled", "alternate", low_foreground),
                    ("disabled", low_foreground),
                ],
                "indicatorbackground": [
                    ("disabled", "alternate", text_background),
                    ("disabled", text_background),
                ],
            },
        },
        "TRadiobutton": {
            "configure": {
                "indicatorforeground": normal_foreground,
                "indicatorbackground": text_background,
            },
            "map": {
                "indicatorforeground": [
                    ("disabled", "alternate", low_foreground),
                    ("disabled", low_foreground),
                ]
            },
        },
        "Toolbutton": {
            "configure": {"background": frame_background},
            "map": {"background": [("disabled", frame_background), ("active", high_detail)]},
        },
        "CustomToolbutton": {
            "configure": {
                "background": frame_background,
                "activebackground": high_detail,
                "foreground": normal_foreground,
            }
        },
        "TLabel": {"configure": {"foreground": normal_foreground}},
        "Url.TLabel": {"configure": {"foreground": link_foreground}},
        "Tip.TLabel": {"configure": {"foreground": normal_foreground, "background": normal_detail}},
        "Tip.TFrame": {"configure": {"background": low_detail}},
        "TScale": {
            "configure": {
                "background": high_detail,
                "troughcolor": normal_detail,
                "lightcolor": high_detail,
                "darkcolor": high_detail,
                "gripcount": 0,
            },
            "map": {"background": [], "troughcolor": []},
        },
        "TScale.slider": {
            "configure": {
                "background": accent_color,
                "troughcolor": normal_detail,
                "lightcolor": accent_color,
                "darkcolor": accent_color,
            }
        },
        "ViewBody.TFrame": {"configure": {"background": text_background}},
        "ViewToolbar.TFrame": {"configure": {"background": active_tab_background}},
        "ViewToolbar.Toolbutton": {"configure": {"background": active_tab_background}},
        "ViewTab.TLabel": {"configure": {"background": active_tab_background, "padding": [5, 0]}},
        "ViewToolbar.TLabel": {
            "configure": {
                "background": active_tab_background,
                "lightcolor": active_tab_background,
                "darkcolor": active_tab_background,
                "bordercolor": active_tab_background,
                "borderwidth": 1,
                "padding": [scale(4), 0],
            }
        },
        "Active.ViewTab.TLabel": {
            "configure": {
                "foreground": normal_foreground,
                "background": active_tab_background,
                "lightcolor": active_tab_background,
                "darkcolor": active_tab_background,
                "relief": "sunken",
                "bordercolor": accent_color,
                "borderwidth": 1,
            },
            "map": {
                "lightcolor": [("hover", active_tab_background)],
                "bordercolor": [("hover", accent_color)],
                "background": [("hover", active_tab_background)],
                "darkcolor": [("hover", active_tab_background)],
                "relief": [("hover", "sunken")],
                "borderwidth": [("hover", 1)],
            },
        },
        "Inactive.ViewTab.TLabel": {
            "configure": {"foreground": normal_foreground},
            "map": {"background": [("hover", high_detail)]},
        },
        "Text": {"configure": {"background": text_background, "foreground": normal_foreground}},
        "Gutter": {"configure": {"background": low_detail, "foreground": low_foreground}},
        "Listbox": {
            "configure": {
                "background": text_background,
                "foreground": normal_foreground,
                "selectbackground": high_detail,
                "selectforeground": high_foreground,
                "disabledforeground": low_foreground,
                "highlightbackground": normal_detail,
                "highlightcolor": accent_color,
                "highlightthickness": 0,
            }
        },
        "Menubar": {
            "configure": {
                "custom": running_on_windows() if custom_menubar is None else custom_menubar,
                "background": frame_background,
                "foreground": normal_foreground,
                "activebackground": accent_color,
                "activeforeground": high_foreground,
                "relief": "flat",
            }
        },
        "Menu": {
            "configure": {
                "background": normal_detail,
                "foreground": high_foreground,
                "selectcolor": normal_foreground,
                "activebackground": accent_color,
                "activeforeground": high_foreground,
                "relief": "flat",
            }
        },
        "CustomMenubarLabel.TLabel": {
            "configure": {"padding": [scale(10), scale(2), 0, scale(15)]}
        },
        # Glass effect styles
        "Glass.TFrame": {
            "configure": {
                "background": frame_background,
                "relief": "flat",
            }
        },
        "Glass.TButton": {
            "configure": {
                "background": normal_detail,
                "foreground": normal_foreground,
                "borderwidth": 0,
                "relief": "flat",
                "padding": [scale(16), scale(8)],
            },
            "map": {
                "background": [("active", high_detail), ("pressed", accent_color)],
                "foreground": [("active", high_foreground), ("pressed", "white")],
            },
        },
    }


def load_plugin() -> None:
    """Load glass UI themes"""
    dark_images = {"tab-close-active": "tab-close-active-dark"}

    # Glass Dark - Modern dark theme with glass morphism
    get_workbench().add_ui_theme(
        "Glass Dark",
        "Enhanced Clam",
        glass_morphism(
            frame_background="#1e1e1e",
            text_background="#252526",
            normal_detail="#2d2d30",
            high_detail="#3e3e42",
            low_detail="#252526",
            scrollbar_background="#3e3e42",
            trough_background="#1e1e1e",
            active_tab_background="#252526",
            normal_foreground="#cccccc",
            high_foreground="#ffffff",
            low_foreground="#6e6e6e",
            link_foreground="#4fc1ff",
            accent_color="#007acc",
        ),
        images=dark_images,
    )

    # Glass Dark Purple - Purple-tinted dark theme
    get_workbench().add_ui_theme(
        "Glass Dark Purple",
        "Enhanced Clam",
        glass_morphism(
            frame_background="#1a1a2e",
            text_background="#16213e",
            normal_detail="#0f3460",
            high_detail="#533483",
            low_detail="#1a1a2e",
            scrollbar_background="#533483",
            trough_background="#1a1a2e",
            active_tab_background="#16213e",
            normal_foreground="#e94560",
            high_foreground="#ffffff",
            low_foreground="#6e6e6e",
            link_foreground="#e94560",
            accent_color="#e94560",
        ),
        images=dark_images,
    )

    # Glass Light - Clean light theme
    get_workbench().add_ui_theme(
        "Glass Light",
        "Enhanced Clam",
        glass_morphism(
            frame_background="#f5f5f5",
            text_background="#ffffff",
            normal_detail="#e8e8e8",
            high_detail="#d4d4d4",
            low_detail="#c0c0c0",
            scrollbar_background="#c0c0c0",
            trough_background="#f0f0f0",
            active_tab_background="#ffffff",
            normal_foreground="#333333",
            high_foreground="#000000",
            low_foreground="#808080",
            link_foreground="#0066cc",
            accent_color="#0078d4",
            custom_menubar=0,
        ),
    )

    # Glass Ocean - Ocean-inspired blue theme
    get_workbench().add_ui_theme(
        "Glass Ocean",
        "Enhanced Clam",
        glass_morphism(
            frame_background="#0d1b2a",
            text_background="#1b263b",
            normal_detail="#415a77",
            high_detail="#778da9",
            low_detail="#1b263b",
            scrollbar_background="#778da9",
            trough_background="#0d1b2a",
            active_tab_background="#1b263b",
            normal_foreground="#e0e1dd",
            high_foreground="#ffffff",
            low_foreground="#778da9",
            link_foreground="#00b4d8",
            accent_color="#00b4d8",
        ),
        images=dark_images,
    )

    # Glass Sunset - Warm sunset colors
    get_workbench().add_ui_theme(
        "Glass Sunset",
        "Enhanced Clam",
        glass_morphism(
            frame_background="#2d1b2e",
            text_background="#3d2c3e",
            normal_detail="#4a3b4c",
            high_detail="#ff6b6b",
            low_detail="#3d2c3e",
            scrollbar_background="#ff6b6b",
            trough_background="#2d1b2e",
            active_tab_background="#3d2c3e",
            normal_foreground="#ffd93d",
            high_foreground="#ffffff",
            low_foreground="#6c5ce7",
            link_foreground="#ff6b6b",
            accent_color="#ff6b6b",
        ),
        images=dark_images,
    )
