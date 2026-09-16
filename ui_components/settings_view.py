from __future__ import annotations

import flet as ft

import config
from localization import Strings
from settings_store import load_settings, save_gemini_key, save_settings
from ui_components.widgets import action_button

BG_CARD = "#172033"
TEXT = "#F8FAFC"
MUTED = "#A8B3C7"
BLUE = "#60A5FA"
TEAL = "#2DD4BF"
FIELD_BG = "#202D43"

MODEL_OPTIONS = [
    ("gfs_seamless", "GFS \u2014 NOAA \u0622\u0645\u0631\u06cc\u06a9\u0627"),
    ("ecmwf_ifs025", "ECMWF \u2014 \u0645\u0631\u06a9\u0632 \u0627\u0631\u0648\u067e\u0627\u06cc\u06cc"),
    ("icon_seamless", "ICON \u2014 \u0633\u0631\u0648\u06cc\u0633 \u0647\u0648\u0627\u0634\u0646\u0627\u0633\u06cc \u0622\u0644\u0645\u0627\u0646"),
]


def _field(label: str, value: str, *, password: bool = False, can_reveal: bool = False) -> ft.TextField:
    """A text field whose value sits on the LEFT so it never collides with the
    right-hand Persian (RTL) label."""
    return ft.TextField(
        label=label,
        value=value,
        password=password,
        can_reveal_password=can_reveal,
        color=TEXT,
        bgcolor=FIELD_BG,
        border_color="#40516D",
        focused_border_color=TEAL,
        text_align=ft.TextAlign.LEFT,
        rtl=False,
        expand=True,
    )


class SettingsView(ft.Container):
    def __init__(self, on_saved=None):
        super().__init__(expand=True, padding=0)
        self.on_saved = on_saved
        settings = load_settings()
        self.favorites = list(settings.get("favorites", []))

        self.favorite_dropdown = ft.Dropdown(
            label="\u0634\u0647\u0631\u0647\u0627\u06cc \u0630\u062e\u06cc\u0631\u0647\u200c\u0634\u062f\u0647",
            options=self._favorite_options(),
            color=TEXT,
            bgcolor=FIELD_BG,
            border_color="#40516D",
            focused_border_color=TEAL,
        )
        self.location_name = _field("\u0646\u0627\u0645 \u0645\u06a9\u0627\u0646", settings["location_name"])
        self.latitude = _field("\u0639\u0631\u0636 \u062c\u063a\u0631\u0627\u0641\u06cc\u0627\u06cc\u06cc", str(settings["latitude"]))
        self.longitude = _field("\u0637\u0648\u0644 \u062c\u063a\u0631\u0627\u0641\u06cc\u0627\u06cc\u06cc", str(settings["longitude"]))
        self.timezone = _field("\u0645\u0646\u0637\u0642\u0647\u200c\u06cc \u0632\u0645\u0627\u0646\u06cc", settings["timezone"])
        self.gemini_key = _field("\u06a9\u0644\u06cc\u062f Gemini (\u0627\u062e\u062a\u06cc\u0627\u0631\u06cc)", "", password=True, can_reveal=True)
        self.gemini_hint = ft.Text(
            "\u06a9\u0644\u06cc\u062f \u062f\u0631 \u0641\u0627\u06cc\u0644 \u062a\u0646\u0638\u06cc\u0645\u0627\u062a \u0630\u062e\u06cc\u0631\u0647 \u0646\u0645\u06cc\u200c\u0634\u0648\u062f \u0648 \u062f\u0631 Windows User Environment \u062b\u0628\u062a \u0645\u06cc\u200c\u0634\u0648\u062f.",
            size=11,
            color=MUTED,
        )

        selected = set(settings["models"])
        self.model_checks = {
            model_id: ft.Checkbox(
                label=label,
                value=model_id in selected,
                fill_color=TEAL,
                check_color="#0F172A",
                label_style=ft.TextStyle(color=TEXT),
            )
            for model_id, label in MODEL_OPTIONS
        }
        self.status = ft.Text("", size=12, color=TEAL)
        self.content = self._build_content()

    def _favorite_options(self) -> list[ft.DropdownOption]:
        return [
            ft.DropdownOption(key=str(index), text=item["name"])
            for index, item in enumerate(self.favorites)
        ]

    def _build_content(self):
        return ft.ListView(
            expand=True,
            padding=4,
            spacing=12,
            controls=[
                ft.Container(
                    padding=18,
                    border_radius=18,
                    bgcolor=BG_CARD,
                    content=ft.Column(
                        controls=[
                            ft.Text(Strings.SETTINGS, size=22, weight=ft.FontWeight.BOLD, color=TEXT),
                            ft.Text("\u062a\u0646\u0638\u06cc\u0645\u0627\u062a \u062f\u0631 \u0647\u0645\u06cc\u0646 \u0633\u06cc\u0633\u062a\u0645 \u0630\u062e\u06cc\u0631\u0647 \u0645\u06cc\u200c\u0634\u0648\u0646\u062f \u0648 \u0631\u0648\u06cc \u067e\u06cc\u0634\u200c\u0628\u06cc\u0646\u06cc\u200c\u0647\u0627\u06cc \u0628\u0639\u062f\u06cc \u0627\u0639\u0645\u0627\u0644 \u062e\u0648\u0627\u0647\u0646\u062f \u0634\u062f.", size=12, color=MUTED),
                            ft.Divider(color="#2B3A55"),
                            self.favorite_dropdown,
                            action_button(
                                "\u0627\u0633\u062a\u0641\u0627\u062f\u0647 \u0627\u0632 \u0634\u0647\u0631 \u0627\u0646\u062a\u062e\u0627\u0628\u200c\u0634\u062f\u0647",
                                on_click=self._use_favorite,
                                bgcolor=TEAL,
                                color="#0F172A",
                                icon=ft.Icons.LOCATION_CITY,
                            ),
                            ft.Text("\u0628\u0627 \u0627\u0646\u062a\u062e\u0627\u0628 \u0634\u0647\u0631\u060c \u0646\u06cc\u0627\u0632\u06cc \u0628\u0647 \u0648\u0627\u0631\u062f\u06a9\u0631\u062f\u0646 \u0645\u062e\u062a\u0635\u0627\u062a \u0631\u0648\u06cc \u0646\u0642\u0634\u0647 \u0646\u06cc\u0633\u062a.", size=11, color=MUTED),
                            ft.Divider(color="#2B3A55"),
                            self.location_name,
                            ft.Row(controls=[self.latitude, self.longitude], spacing=8),
                            self.timezone,
                            action_button(
                                Strings.SAVE_FAVORITE,
                                on_click=self._save_favorite,
                                bgcolor="#F59E0B",
                                color="#0F172A",
                                icon=ft.Icons.STAR,
                                tooltip="\u0630\u062e\u06cc\u0631\u0647\u200c\u06cc \u0634\u0647\u0631 \u0641\u0639\u0644\u06cc \u0628\u0631\u0627\u06cc \u062f\u0633\u062a\u0631\u0633\u06cc \u0633\u0631\u06cc\u0639 \u062f\u0631 \u0622\u06cc\u0646\u062f\u0647",
                            ),
                            ft.Text("\u0645\u062f\u0644\u200c\u0647\u0627\u06cc \u067e\u06cc\u0634\u200c\u0628\u06cc\u0646\u06cc", size=16, weight=ft.FontWeight.BOLD, color=TEXT),
                            ft.Column(controls=list(self.model_checks.values()), spacing=0),
                            ft.Divider(color="#2B3A55"),
                            ft.Text("\u0627\u062a\u0635\u0627\u0644 Gemini", size=16, weight=ft.FontWeight.BOLD, color=TEXT),
                            ft.Text(
                                "\u0648\u0636\u0639\u06cc\u062a \u0641\u0639\u0644\u06cc: " + ("\u06a9\u0644\u06cc\u062f \u062a\u0646\u0638\u06cc\u0645 \u0634\u062f\u0647 \u0627\u0633\u062a." if config.GEMINI_API_KEY else "\u06a9\u0644\u06cc\u062f\u06cc \u062a\u0646\u0638\u06cc\u0645 \u0646\u0634\u062f\u0647 \u0627\u0633\u062a."),
                                size=12,
                                color=TEAL if config.GEMINI_API_KEY else "#FBBF24",
                            ),
                            self.gemini_key,
                            self.gemini_hint,
                            action_button(
                                Strings.SAVE_SETTINGS,
                                on_click=self._save,
                                bgcolor=BLUE,
                                color="#FFFFFF",
                                icon=ft.Icons.SAVE,
                            ),
                            self.status,
                        ],
                        spacing=12,
                    ),
                )
            ],
        )

    def _set_status(self, message: str, color: str) -> None:
        self.status.value = message
        self.status.color = color
        self._safe_update()

    def _safe_update(self) -> None:
        try:
            page = self.page
        except (RuntimeError, AssertionError):
            page = None
        if page:
            page.update()

    def _use_favorite(self, event=None):
        try:
            index = int(self.favorite_dropdown.value)
            favorite = self.favorites[index]
            self.location_name.value = favorite["name"]
            self.latitude.value = str(favorite["latitude"])
            self.longitude.value = str(favorite["longitude"])
            self.timezone.value = favorite["timezone"]
            self._save()
        except (TypeError, ValueError, IndexError):
            self._set_status("\u0627\u0628\u062a\u062f\u0627 \u06cc\u06a9 \u0634\u0647\u0631 \u0631\u0627 \u0627\u0646\u062a\u062e\u0627\u0628 \u06a9\u0646\u06cc\u062f.", "#FBBF24")

    def _save_favorite(self, event=None):
        """Persist the currently entered city so it can be reused later."""
        name = (self.location_name.value or "").strip()
        try:
            latitude = float(self.latitude.value)
            longitude = float(self.longitude.value)
        except (TypeError, ValueError):
            self._set_status(Strings.FAVORITE_NEEDS_NAME, "#F87171")
            return
        if not name:
            self._set_status(Strings.FAVORITE_NEEDS_NAME, "#F87171")
            return

        timezone = (self.timezone.value or "Asia/Tehran").strip()
        for item in self.favorites:
            same_name = item.get("name", "").strip() == name
            same_coords = (
                abs(float(item.get("latitude", 0)) - latitude) < 1e-4
                and abs(float(item.get("longitude", 0)) - longitude) < 1e-4
            )
            if same_name or same_coords:
                self._set_status(Strings.FAVORITE_EXISTS, "#FBBF24")
                return

        self.favorites.append(
            {"name": name, "latitude": latitude, "longitude": longitude, "timezone": timezone}
        )
        save_settings({
            "location_name": name,
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone,
            "models": self._selected_models() or None,
            "favorites": self.favorites,
        })
        self.favorite_dropdown.options = self._favorite_options()
        self.favorite_dropdown.value = str(len(self.favorites) - 1)
        self._set_status(Strings.FAVORITE_SAVED, TEAL)

    def _selected_models(self):
        return [model_id for model_id, _ in MODEL_OPTIONS if self.model_checks[model_id].value]

    def _save(self, event=None):
        try:
            selected_models = self._selected_models()
            if not selected_models:
                self._set_status("\u062d\u062f\u0627\u0642\u0644 \u06cc\u06a9 \u0645\u062f\u0644 \u0631\u0627 \u0627\u0646\u062a\u062e\u0627\u0628 \u06a9\u0646\u06cc\u062f.", "#F87171")
                return
            settings = save_settings({
                "location_name": self.location_name.value,
                "latitude": self.latitude.value,
                "longitude": self.longitude.value,
                "timezone": self.timezone.value,
                "models": selected_models,
                "favorites": self.favorites,
            })
            if self.gemini_key.value.strip():
                save_gemini_key(self.gemini_key.value)
                config.GEMINI_API_KEY = self.gemini_key.value.strip()
            self._set_status(f"\u062a\u0646\u0638\u06cc\u0645\u0627\u062a \u0630\u062e\u06cc\u0631\u0647 \u0634\u062f: {settings['location_name']}", TEAL)
            if self.on_saved:
                self.on_saved(settings)
        except (TypeError, ValueError):
            self._set_status("\u0645\u062e\u062a\u0635\u0627\u062a \u062c\u063a\u0631\u0627\u0641\u06cc\u0627\u06cc\u06cc \u0645\u0639\u062a\u0628\u0631 \u0646\u06cc\u0633\u062a\u0646\u062f.", "#F87171")
