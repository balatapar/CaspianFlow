from __future__ import annotations

import flet as ft
import flet_charts as fc

from utils import format_date, format_temperature, to_persian_digits


TEXT = "#f0e8d5"
MUTED = "#b8ad93"
BLUE = "#a3b18a"
RED = "#e6c656"
TEAL = "#7fb069"


def _short_dates(values: list[str]) -> list[str]:
    return [format_date(value, include_weekday=False) for value in values]


def build_weather_charts(daily: dict) -> ft.Container:
    """Build compact temperature and precipitation charts for the 7-day data."""
    dates = daily.get("time", [])[:7]
    maximums = [float(v) for v in daily.get("temperature_2m_max", [])[:7]]
    minimums = [float(v) for v in daily.get("temperature_2m_min", [])[:7]]
    precipitation = [float(v or 0) for v in daily.get("precipitation_sum", [])[:7]]

    if not dates or not maximums or not minimums:
        return ft.Container()

    labels = _short_dates(dates)
    min_temp = min(minimums) - 2
    max_temp = max(maximums) + 2
    points_max = [
        fc.LineChartDataPoint(x=index, y=value, tooltip=f"{labels[index]}: {format_temperature(value)}")
        for index, value in enumerate(maximums)
    ]
    points_min = [
        fc.LineChartDataPoint(x=index, y=value, tooltip=f"{labels[index]}: {format_temperature(value)}")
        for index, value in enumerate(minimums)
    ]
    temperature_chart = fc.LineChart(
        data_series=[
            fc.LineChartData(points=points_max, color=RED, curved=True, stroke_width=3, point=True),
            fc.LineChartData(points=points_min, color=BLUE, curved=True, stroke_width=3, point=True),
        ],
        min_x=0,
        max_x=max(1, len(dates) - 1),
        min_y=min_temp,
        max_y=max_temp,
        height=210,
        interactive=True,
        bgcolor="#353d31",
        # Keep the tooltip inside the chart box so the first/last day are readable.
        tooltip=fc.LineChartTooltip(
            fit_inside_horizontally=True,
            fit_inside_vertically=True,
            bgcolor="#1c201a",
        ),
    )

    max_rain = max(max(precipitation), 1)
    rain_groups = [
        fc.BarChartGroup(
            x=index,
            rods=[
                fc.BarChartRod(
                    to_y=value,
                    color=TEAL,
                    width=18,
                    border_radius=4,
                    tooltip="",
                )
            ],
        )
        for index, value in enumerate(precipitation)
    ]
    # Replace the generated tooltip expression with Persian-formatted values.
    for index, group in enumerate(rain_groups):
        value = precipitation[index]
        group.rods[0].tooltip = f"{labels[index]}: {to_persian_digits(round(value, 1))} \u0645\u06cc\u0644\u06cc\u200c\u0645\u062a\u0631"

    rain_chart = fc.BarChart(
        groups=rain_groups,
        min_y=0,
        max_y=max_rain + max(1, max_rain * 0.15),
        height=190,
        interactive=True,
        bgcolor="#353d31",
        # Keep bar tooltips from spilling off the left/right edges.
        tooltip=fc.BarChartTooltip(
            fit_inside_horizontally=True,
            fit_inside_vertically=True,
            bgcolor="#1c201a",
        ),
    )

    def chart_card(title: str, chart: ft.Control, legend: list[tuple[str, str]]) -> ft.Container:
        return ft.Container(
            padding=12,
            border_radius=16,
            bgcolor="#353d31",
            content=ft.Column(
                controls=[
                    ft.Text(title, size=17, weight=ft.FontWeight.BOLD, color=TEXT),
                    chart,
                    ft.Row(
                        controls=[
                            ft.Row(
                                controls=[ft.Container(width=10, height=10, bgcolor=color, border_radius=5), ft.Text(label, size=11, color=MUTED)],
                                spacing=5,
                            )
                            for color, label in legend
                        ],
                        spacing=14,
                    ),
                ],
                spacing=8,
            ),
        )

    return ft.Column(
        controls=[
            chart_card("\u0631\u0648\u0646\u062f \u062f\u0645\u0627", temperature_chart, [(RED, "\u0628\u06cc\u0634\u06cc\u0646\u0647"), (BLUE, "\u06a9\u0645\u06cc\u0646\u0647")]),
            chart_card("\u0628\u0627\u0631\u0634 \u0631\u0648\u0632\u0627\u0646\u0647", rain_chart, [(TEAL, "\u0645\u06cc\u0644\u06cc\u200c\u0645\u062a\u0631")]),
        ],
        spacing=12,
    )
