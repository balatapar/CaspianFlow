from __future__ import annotations

import requests

from config import FORECAST_DAYS, OPEN_METEO_BASE_URL, REQUEST_TIMEOUT_SECONDS
from settings_store import load_settings


def get_daily_and_hourly_weather(
    latitude: float | None = None,
    longitude: float | None = None,
    timezone: str | None = None,
) -> dict:
    """Fetch the data needed by the dashboard from Open-Meteo."""
    settings = load_settings()
    latitude = settings["latitude"] if latitude is None else latitude
    longitude = settings["longitude"] if longitude is None else longitude
    timezone = settings["timezone"] if timezone is None else timezone

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": ",".join(
            [
                "temperature_2m",
                "relative_humidity_2m",
                "apparent_temperature",
                "is_day",
                "precipitation",
                "weather_code",
                "wind_speed_10m",
                "wind_direction_10m",
            ]
        ),
        "hourly": ",".join(
            [
                "temperature_2m",
                "relative_humidity_2m",
                "wind_speed_10m",
                "precipitation_probability",
                "precipitation",
                "weather_code",
            ]
        ),
        "daily": ",".join(
            [
                "weather_code",
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_sum",
                "precipitation_probability_max",
                "wind_speed_10m_max",
            ]
        ),
        "temperature_unit": "celsius",
        "wind_speed_unit": "kmh",
        "precipitation_unit": "mm",
        "timezone": timezone,
        "forecast_days": FORECAST_DAYS,
    }

    response = requests.get(
        OPEN_METEO_BASE_URL,
        params=params,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()
