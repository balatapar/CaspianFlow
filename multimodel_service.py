from __future__ import annotations

import requests

from config import FORECAST_DAYS, OPEN_METEO_BASE_URL, REQUEST_TIMEOUT_SECONDS
from settings_store import load_settings


WEATHER_MODELS = {
    "gfs_seamless": "GFS (NOAA آمریکا)",
    "ecmwf_ifs025": "ECMWF (مرکز اروپایی)",
    "icon_seamless": "ICON (سرویس هواشناسی آلمان)",
}

MODEL_VARIABLES = (
    "temperature_2m",
    "precipitation_probability",
    "pressure_msl",
)

DAILY_VARIABLES = (
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "precipitation_probability_max",
)


def get_multi_model_forecast(
    latitude: float | None = None,
    longitude: float | None = None,
    timezone: str | None = None,
    model_ids: list[str] | None = None,
) -> dict:
    """Fetch the selected weather models in one Open-Meteo request."""
    settings = load_settings()
    latitude = settings["latitude"] if latitude is None else latitude
    longitude = settings["longitude"] if longitude is None else longitude
    timezone = settings["timezone"] if timezone is None else timezone
    selected_ids = [model for model in (model_ids or settings["models"]) if model in WEATHER_MODELS]
    if not selected_ids:
        selected_ids = list(WEATHER_MODELS)

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ",".join(MODEL_VARIABLES),
        "daily": ",".join(DAILY_VARIABLES),
        "models": ",".join(selected_ids),
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
    payload = response.json()
    daily = payload.get("daily", {})
    hourly = payload.get("hourly", {})

    models = {}
    for model_id in selected_ids:
        label = WEATHER_MODELS[model_id]
        models[model_id] = {
            "label": label,
            "daily": {
                "time": daily.get("time", []),
                "temperature_max": daily.get(f"temperature_2m_max_{model_id}", []),
                "temperature_min": daily.get(f"temperature_2m_min_{model_id}", []),
                "precipitation_sum": daily.get(f"precipitation_sum_{model_id}", []),
                "precipitation_probability": daily.get(
                    f"precipitation_probability_max_{model_id}", []
                ),
            },
            "hourly": {
                "time": hourly.get("time", []),
                "temperature": hourly.get(f"temperature_2m_{model_id}", []),
                "precipitation_probability": hourly.get(
                    f"precipitation_probability_{model_id}", []
                ),
                "pressure_msl": hourly.get(f"pressure_msl_{model_id}", []),
            },
        }

    return {
        "location": settings["location_name"],
        "latitude": latitude,
        "longitude": longitude,
        "timezone": payload.get("timezone", timezone),
        "source": "Open-Meteo",
        "models": models,
    }
