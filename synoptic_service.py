from __future__ import annotations

from statistics import mean

import requests

from config import OPEN_METEO_BASE_URL, REQUEST_TIMEOUT_SECONDS
from settings_store import load_settings


SYNOPTIC_POINTS = {
    "سیبری غربی": (60.0, 90.0),
    "اروپای مرکزی": (50.0, 10.0),
    "اطلس شمالی": (50.0, -30.0),
}


SYNOPTIC_VARIABLES = (
    "pressure_msl",
    "geopotential_height_500hPa",
    "geopotential_height_850hPa",
)


def _summarize_point(payload: dict, name: str, coordinates: tuple[float, float]) -> dict:
    hourly = payload.get("hourly", {})
    times = hourly.get("time", [])

    def values(key: str) -> list[float]:
        return [float(value) for value in hourly.get(key, []) if value is not None]

    pressure = values("pressure_msl")
    height_500 = values("geopotential_height_500hPa")
    height_850 = values("geopotential_height_850hPa")
    sample_indexes = list(range(0, min(len(times), 7 * 24), 24))

    return {
        "name": name,
        "latitude": coordinates[0],
        "longitude": coordinates[1],
        "timezone": payload.get("timezone"),
        "sample_times": [times[i] for i in sample_indexes],
        "pressure_msl_hpa": {
            "first": round(pressure[0], 1) if pressure else None,
            "min_7d": round(min(pressure), 1) if pressure else None,
            "max_7d": round(max(pressure), 1) if pressure else None,
            "mean_7d": round(mean(pressure), 1) if pressure else None,
        },
        "geopotential_height_500hPa_m": {
            "first": round(height_500[0], 1) if height_500 else None,
            "mean_7d": round(mean(height_500), 1) if height_500 else None,
        },
        "geopotential_height_850hPa_m": {
            "first": round(height_850[0], 1) if height_850 else None,
            "mean_7d": round(mean(height_850), 1) if height_850 else None,
        },
    }


def get_synoptic_context() -> dict:
    """Fetch coarse synoptic indicators for the selected location and upstream areas."""
    settings = load_settings()
    points = {settings["location_name"]: (settings["latitude"], settings["longitude"]), **SYNOPTIC_POINTS}
    coordinates = list(points.values())
    params = {
        "latitude": ",".join(str(item[0]) for item in coordinates),
        "longitude": ",".join(str(item[1]) for item in coordinates),
        "hourly": ",".join(SYNOPTIC_VARIABLES),
        "timezone": "UTC",
        "forecast_days": 7,
    }
    response = requests.get(
        OPEN_METEO_BASE_URL,
        params=params,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    payloads = response.json()
    if not isinstance(payloads, list):
        payloads = [payloads]

    return {
        "source": "Open-Meteo forecast model fields",
        "variables": list(SYNOPTIC_VARIABLES),
        "regions": [
            _summarize_point(payload, name, coordinates[index])
            for index, (name, _) in enumerate(points.items())
            for payload in payloads[index : index + 1]
        ],
    }
