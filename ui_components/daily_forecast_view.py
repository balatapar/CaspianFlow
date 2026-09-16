from __future__ import annotations

import asyncio

import flet as ft

from localization import Strings
from settings_store import load_settings
from ui_components.weather_charts import build_weather_charts
from ui_components.widgets import action_button
from utils import (
    format_date,
    format_hour,
    format_percentage,
    format_precipitation,
    format_temperature,
    format_wind_speed,
)
from weather_service import get_daily_and_hourly_weather


CARD = "#172033"
TEXT = "#F8FAFC"
MUTED = "#A8B3C7"
BLUE = "#60A5FA"
TEAL = "#2DD4BF"


WEATHER_LABELS = {
    0: "\u0622\u0633\u0645\u0627\u0646 \u0635\u0627\u0641",
    1: "\u06a9\u0645\u06cc \u0627\u0628\u0631\u06cc",
    2: "\u0646\u06cc\u0645\u0647\u200c\u0627\u0628\u0631\u06cc",
    3: "\u0627\u0628\u0631\u06cc",
    45: "\u0645\u0647\u200c\u0622\u0644\u0648\u062f",
    48: "\u0645\u0647 \u06cc\u062e\u200c\u0632\u062f\u0647",
    51: "\u0646\u0645\u200c\u0646\u0645 \u0628\u0627\u0631\u0627\u0646",
    53: "\u0628\u0627\u0631\u0634 \u067e\u0631\u0627\u06a9\u0646\u062f\u0647",
    55: "\u0628\u0627\u0631\u0634 \u0646\u0645\u200c\u0646\u0645 \u0634\u062f\u06cc\u062f",
    61: "\u0628\u0627\u0631\u0627\u0646 \u0633\u0628\u06a9",
    63: "\u0628\u0627\u0631\u0627\u0646",
    65: "\u0628\u0627\u0631\u0627\u0646 \u0634\u062f\u06cc\u062f",
    71: "\u0628\u0631\u0641 \u0633\u0628\u06a9",
    73: "\u0628\u0631\u0641",
    75: "\u0628\u0631\u0641 \u0634\u062f\u06cc\u062f",
    80: "\u0631\u06af\u0628\u0627\u0631 \u067e\u0631\u0627\u06a9\u0646\u062f\u0647",
    81: "\u0631\u06af\u0628\u0627\u0631",
    82: "\u0631\u06af\u0628\u0627\u0631 \u0634\u062f\u06cc\u062f",
    95: "\u0631\u0639\u062f\u0648\u0628\u0631\u0642",
    96: "\u0631\u0639\u062f\u0648\u0628\u0631\u0642 \u0648 \u062a\u06af\u0631\u06af",
    99: "\u0631\u0639\u062f\u0648\u0628\u0631\u0642 \u0648 \u062a\u06af\u0631\u06af \u0634\u062f\u06cc\u062f",
}


def weather_label(code: int | None) -> str:
    return WEATHER_LABELS.get(code, "\u0648\u0636\u0639\u06cc\u062a \u062c\u0648\u06cc \u0646\u0627\u0645\u0634\u062e\u0635")


def metric(label: str, value: str) -> ft.Container:
    return ft.Container(
        padding=10,
        border_radius=12,
        bgcolor="#202D43",
        expand=True,
        content=ft.Column(
            controls=[
                ft.Text(label, size=12, color=MUTED),
                ft.Text(value, size=16, weight=ft.FontWeight.BOLD, color=TEXT),
            ],
            spacing=3,
        ),
    )


def surface(content: ft.Control, padding: int = 16) -> ft.Container:
    return ft.Container(
        content=content,
        padding=padding,
        border_radius=18,
        bgcolor=CARD,
        shadow=ft.BoxShadow(blur_radius=14, color="#30000000", offset=ft.Offset(0, 4)),
    )


class DailyForecastView(ft.Container):
    def __init__(self):
        super().__init__(expand=True, padding=0)
        self.content = ft.Column(
            controls=[ft.ProgressRing(), ft.Text(Strings.LOADING, color=MUTED)],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        )

    def _header(self) -> ft.Container:
        """Title + refresh button, so switching city can be re-fetched on demand."""
        return surface(
            ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text(Strings.DAILY_FORECAST, size=18, weight=ft.FontWeight.BOLD, color=TEXT),
                            ft.Text(load_settings()["location_name"], size=13, color=MUTED),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    action_button(
                        Strings.REFRESH,
                        on_click=lambda event: asyncio.create_task(self.load_weather_data()),
                        bgcolor=TEAL,
                        color="#0F172A",
                        icon=ft.Icons.REFRESH,
                        tooltip=Strings.REFRESH_HINT,
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=12,
        )

    def _current_card(self, data: dict) -> ft.Container:
        current = data.get("current", data.get("current_weather", {}))
        temp = current.get("temperature_2m", current.get("temperature"))
        humidity = current.get("relative_humidity_2m")
        wind = current.get("wind_speed_10m", current.get("windspeed"))
        rain = current.get("precipitation", 0)
        current_time = current.get("time")
        code = current.get("weather_code")
        if code is None:
            code = current.get("weathercode")

        return surface(
            ft.Column(
                controls=[
                    ft.Row(controls=[ft.Text(Strings.CURRENT_CONDITIONS, size=14, color=MUTED, expand=True), ft.Text(format_date(current_time) if current_time else "", size=12, color=MUTED)]),
                    ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text(format_temperature(temp), size=42, weight=ft.FontWeight.BOLD, color=TEXT),
                                    ft.Text(weather_label(code), size=16, color=TEXT),
                                ],
                                spacing=2,
                            ),
                            ft.Text("\u2601\ufe0f", size=48),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Row(
                        controls=[
                            metric(Strings.FEELS_LIKE, format_temperature(current.get("apparent_temperature"))),
                            metric(Strings.HUMIDITY, format_percentage(humidity)),
                            metric(Strings.WIND, format_wind_speed(wind)),
                        ],
                        spacing=8,
                    ),
                    ft.Text(f"\u0628\u0627\u0631\u0634 \u0641\u0639\u0644\u06cc: {format_precipitation(rain)}", size=12, color=MUTED),
                ],
                spacing=12,
            )
        )

    def _daily_card(self, daily: dict, index: int) -> ft.Container:
        probability = (daily.get("precipitation_probability_max") or [0])[index]
        maximum = daily.get("temperature_2m_max", [None])[index]
        minimum = daily.get("temperature_2m_min", [None])[index]
        rain = daily.get("precipitation_sum", [None])[index]
        wind = daily.get("wind_speed_10m_max", [None])[index]
        code = (daily.get("weather_code") or [None])[index]
        date = daily.get("time", [""])[index]

        return surface(
            ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(format_date(date), weight=ft.FontWeight.BOLD, color=TEXT, expand=True),
                            ft.Text(weather_label(code), size=12, color=MUTED),
                        ]
                    ),
                    ft.Row(
                        controls=[
                            ft.Text(f"{Strings.MAX}: {format_temperature(maximum)}", color="#D04A4A"),
                            ft.Text(f"{Strings.MIN}: {format_temperature(minimum)}", color=BLUE),
                            ft.Text(f"{Strings.WIND}: {format_wind_speed(wind)}", size=12, color=MUTED),
                        ],
                        wrap=True,
                    ),
                    ft.Row(
                        controls=[
                            ft.Text(f"{Strings.PRECIPITATION}: {format_precipitation(rain)}", size=12, color=MUTED),
                            ft.Text(f"{Strings.PRECIPITATION_PROBABILITY}: {format_percentage(probability)}", size=12, color=MUTED),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.ProgressBar(value=max(0, min(1, (probability or 0) / 100)), color=TEAL, bgcolor="#E8EEF5"),
                ],
                spacing=8,
            )
        )

    def _hourly_section(self, hourly: dict, start_time: str | None = None) -> ft.Container:
        all_times = hourly.get("time", [])
        start_index = 0
        if start_time and all_times:
            start_index = next((i for i, value in enumerate(all_times) if value >= start_time), 0)
        times = all_times[start_index:start_index + 12]
        temperatures = hourly.get("temperature_2m", [])[start_index:start_index + 12]
        probabilities = hourly.get("precipitation_probability", [])[start_index:start_index + 12]
        controls = []
        for index, time in enumerate(times):
            probability = probabilities[index] if index < len(probabilities) else 0
            temperature = temperatures[index] if index < len(temperatures) else None
            controls.append(
                ft.Container(
                    width=82,
                    padding=8,
                    border_radius=12,
                    bgcolor="#202D43",
                    content=ft.Column(
                        controls=[
                            ft.Text(format_hour(time), size=11, color=MUTED, text_align=ft.TextAlign.CENTER),
                            ft.Text(format_temperature(temperature), size=17, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                            ft.Text(f"\u2602 {format_percentage(probability)}", size=11, color=TEAL, text_align=ft.TextAlign.CENTER),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=5,
                    ),
                )
            )
        return surface(
            ft.Column(
                controls=[ft.Text(Strings.HOURLY_FORECAST, size=18, weight=ft.FontWeight.BOLD, color=TEXT), ft.Row(controls=controls, scroll=ft.ScrollMode.AUTO)],
                spacing=12,
            )
        )

    async def load_weather_data(self):
        # Show a loading state while re-fetching (e.g. after switching city).
        self.content = ft.Column(
            controls=[ft.ProgressRing(), ft.Text(Strings.LOADING, color=MUTED)],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        )
        if self.page:
            self.page.update()
        try:
            data = await asyncio.to_thread(get_daily_and_hourly_weather)
            daily = data.get("daily", {})
            self.content = ft.ListView(
                expand=True,
                spacing=12,
                padding=4,
                controls=[
                    self._header(),
                    self._current_card(data),
                    self._hourly_section(data.get("hourly", {}), data.get("current", {}).get("time")),
                    build_weather_charts(daily),
                    ft.Text(Strings.DAILY_FORECAST, size=20, weight=ft.FontWeight.BOLD, color=TEXT),
                    *[self._daily_card(daily, i) for i in range(min(7, len(daily.get("time", []))))],
                ],
            )
        except Exception:
            self.content = ft.Container(
                alignment=ft.Alignment.CENTER,
                content=ft.Text(Strings.ERROR_FETCHING_WEATHER, color="#B42318", text_align=ft.TextAlign.CENTER),
            )
        if self.page:
            self.page.update()
