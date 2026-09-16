from __future__ import annotations

from datetime import datetime


PERSIAN_WEEKDAYS = (
    "دوشنبه",
    "سه‌شنبه",
    "چهارشنبه",
    "پنج‌شنبه",
    "جمعه",
    "شنبه",
    "یکشنبه",
)


def to_persian_digits(value: object) -> str:
    return str(value).translate(str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹"))


def format_date(date_str: str, include_weekday: bool = True) -> str:
    try:
        date = datetime.fromisoformat(date_str).date()
        date_text = to_persian_digits(date.strftime("%Y/%m/%d"))
        if include_weekday:
            return f"{PERSIAN_WEEKDAYS[date.weekday()]}، {date_text}"
        return date_text
    except (TypeError, ValueError):
        return str(date_str)


def format_hour(date_str: str) -> str:
    try:
        return to_persian_digits(datetime.fromisoformat(date_str).strftime("%H:%M"))
    except (TypeError, ValueError):
        return str(date_str)


def format_temperature(value: float | None) -> str:
    return "—" if value is None else f"{to_persian_digits(round(value))}°"


def format_percentage(value: float | None) -> str:
    return "—" if value is None else f"{to_persian_digits(round(value))}%"


def format_wind_speed(value: float | None) -> str:
    return "—" if value is None else f"{to_persian_digits(round(value))} km/h"


def format_precipitation(value: float | None) -> str:
    return "—" if value is None else f"{to_persian_digits(round(value, 1))} mm"
