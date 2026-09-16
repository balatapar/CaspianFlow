from __future__ import annotations

import flet as ft

# Shared palette (kept in sync with the individual views).
BLUE = "#60A5FA"
BLUE_HOVER = "#3B82F6"
TEAL = "#2DD4BF"
TEAL_HOVER = "#14B8A6"
DARK = "#0F172A"
WHITE = "#FFFFFF"


def hover_button(
    text: str,
    on_click,
    base_bg: str = BLUE,
    hover_bg: str = BLUE_HOVER,
    fg: str = WHITE,
    **kwargs,
) -> ft.Button:
    """A Button that visibly lifts and brightens on hover so clicks feel responsive.

    Uses per-ControlState maps for bgcolor/elevation/overlay so the control
    reacts to HOVERED and PRESSED without manual event handlers.
    """
    style = ft.ButtonStyle(
        bgcolor={
            ft.ControlState.DEFAULT: base_bg,
            ft.ControlState.HOVERED: hover_bg,
            ft.ControlState.PRESSED: hover_bg,
        },
        color={
            ft.ControlState.DEFAULT: fg,
            ft.ControlState.HOVERED: fg,
            ft.ControlState.PRESSED: fg,
        },
        elevation={
            ft.ControlState.DEFAULT: 1,
            ft.ControlState.HOVERED: 8,
            ft.ControlState.PRESSED: 2,
        },
        overlay_color={
            ft.ControlState.HOVERED: "#26FFFFFF",
            ft.ControlState.PRESSED: "#40FFFFFF",
        },
        animation_duration=150,
    )
    return ft.Button(content=text, on_click=on_click, style=style, **kwargs)
