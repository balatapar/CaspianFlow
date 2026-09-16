from __future__ import annotations

import flet as ft


def action_button(
    text: str,
    on_click,
    *,
    bgcolor: str = "#60A5FA",
    color: str = "#0F172A",
    hover_bgcolor: str | None = None,
    icon: str | None = None,
    tooltip: str | None = None,
) -> ft.Button:
    """Primary action button with a clear hover state.

    On hover the button lifts (higher elevation) and its background brightens,
    so a single click is obviously registered without repeated taps.
    """
    hover_bg = hover_bgcolor or _lighten(bgcolor)
    style = ft.ButtonStyle(
        bgcolor={
            ft.ControlState.DEFAULT: bgcolor,
            ft.ControlState.HOVERED: hover_bg,
            ft.ControlState.PRESSED: _darken(bgcolor),
        },
        color={ft.ControlState.DEFAULT: color},
        elevation={
            ft.ControlState.DEFAULT: 1,
            ft.ControlState.HOVERED: 8,
            ft.ControlState.PRESSED: 2,
        },
        overlay_color={
            ft.ControlState.HOVERED: "#22FFFFFF",
            ft.ControlState.PRESSED: "#33FFFFFF",
        },
        animation_duration=150,
        padding=ft.Padding(left=18, right=18, top=12, bottom=12),
        mouse_cursor=ft.MouseCursor.CLICK,
    )
    return ft.Button(
        content=text,
        icon=icon,
        on_click=on_click,
        style=style,
        tooltip=tooltip,
    )


def _clamp(value: int) -> int:
    return max(0, min(255, value))


def _shift(hex_color: str, delta: int) -> str:
    color = hex_color.lstrip("#")
    if len(color) != 6:
        return hex_color
    r = _clamp(int(color[0:2], 16) + delta)
    g = _clamp(int(color[2:4], 16) + delta)
    b = _clamp(int(color[4:6], 16) + delta)
    return f"#{r:02X}{g:02X}{b:02X}"


def _lighten(hex_color: str) -> str:
    return _shift(hex_color, 28)


def _darken(hex_color: str) -> str:
    return _shift(hex_color, -28)
