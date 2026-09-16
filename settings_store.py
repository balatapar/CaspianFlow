from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

SETTINGS_PATH = Path(os.getenv("LOCALAPPDATA", Path.home())) / "CaspianWeather" / "settings.json"

DEFAULT_FAVORITES = [
    {"name": "نوشهر، مازندران", "latitude": 36.65, "longitude": 51.50, "timezone": "Asia/Tehran"},
    {"name": "تهران", "latitude": 35.6892, "longitude": 51.3890, "timezone": "Asia/Tehran"},
    {"name": "رشت، گیلان", "latitude": 37.2808, "longitude": 49.5832, "timezone": "Asia/Tehran"},
]

DEFAULT_SETTINGS = {
    "location_name": DEFAULT_FAVORITES[0]["name"],
    "latitude": DEFAULT_FAVORITES[0]["latitude"],
    "longitude": DEFAULT_FAVORITES[0]["longitude"],
    "timezone": DEFAULT_FAVORITES[0]["timezone"],
    "models": ["gfs_seamless", "ecmwf_ifs025", "icon_seamless"],
    "favorites": DEFAULT_FAVORITES,
}


def load_settings() -> dict[str, Any]:
    try:
        with SETTINGS_PATH.open("r", encoding="utf-8") as file:
            data = json.load(file)
        settings = DEFAULT_SETTINGS.copy()
        settings.update(data if isinstance(data, dict) else {})
        return _validate(settings)
    except (OSError, json.JSONDecodeError, TypeError):
        return DEFAULT_SETTINGS.copy()


def save_settings(settings: dict[str, Any]) -> dict[str, Any]:
    validated = _validate({**DEFAULT_SETTINGS, **settings})
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary = SETTINGS_PATH.with_suffix(".tmp")
    with temporary.open("w", encoding="utf-8") as file:
        json.dump(validated, file, ensure_ascii=False, indent=2)
    temporary.replace(SETTINGS_PATH)
    return validated


def _validate(settings: dict[str, Any]) -> dict[str, Any]:
    try:
        latitude = float(settings["latitude"])
        longitude = float(settings["longitude"])
        if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
            raise ValueError
    except (KeyError, TypeError, ValueError):
        latitude = DEFAULT_SETTINGS["latitude"]
        longitude = DEFAULT_SETTINGS["longitude"]

    models = settings.get("models", DEFAULT_SETTINGS["models"])
    valid_models = {"gfs_seamless", "ecmwf_ifs025", "icon_seamless"}
    models = [model for model in models if model in valid_models] if isinstance(models, list) else []
    if not models:
        models = DEFAULT_SETTINGS["models"].copy()

    favorites = settings.get("favorites", DEFAULT_FAVORITES)
    if not isinstance(favorites, list) or not favorites:
        favorites = DEFAULT_FAVORITES.copy()

    return {
        "location_name": str(settings.get("location_name") or DEFAULT_SETTINGS["location_name"]).strip(),
        "latitude": latitude,
        "longitude": longitude,
        "timezone": str(settings.get("timezone") or DEFAULT_SETTINGS["timezone"]).strip(),
        "models": models,
        "favorites": favorites,
    }


def reset_to_default_location() -> dict[str, Any]:
    settings = load_settings()
    default = DEFAULT_FAVORITES[0]
    settings.update({
        "location_name": default["name"],
        "latitude": default["latitude"],
        "longitude": default["longitude"],
        "timezone": default["timezone"],
    })
    return save_settings(settings)


def save_gemini_key(key: str) -> None:
    """Save the key to the current process and Windows User environment."""
    key = key.strip()
    if not key:
        return
    os.environ["GEMINI_API_KEY"] = key
    if os.name == "nt":
        import winreg

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_SET_VALUE) as registry:
            winreg.SetValueEx(registry, "GEMINI_API_KEY", 0, winreg.REG_SZ, key)
