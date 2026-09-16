from __future__ import annotations

import json

from google import genai

import config
from localization import Strings
from settings_store import load_settings


def _compact_weather_payload(raw_weather_data: dict, synoptic_context: dict | None = None) -> dict:
    """Keep the prompt small and make the model's input explicit."""
    settings = load_settings()
    return {
        "location": settings["location_name"],
        "latitude": settings["latitude"],
        "longitude": settings["longitude"],
        "timezone": raw_weather_data.get("timezone"),
        "current": raw_weather_data.get("current", raw_weather_data.get("current_weather", {})),
        "daily": raw_weather_data.get("daily", {}),
        "synoptic_context": synoptic_context or {},
    }


def get_weekly_synoptic_analysis(
    raw_weather_data: dict,
    synoptic_context: dict | None = None,
) -> str:
    """Generate a cautious, plain-Persian weekly interpretation with Gemini."""
    if not config.GEMINI_API_KEY:
        return Strings.ANALYSIS_NOT_CONFIGURED

    weather_payload = json.dumps(
        _compact_weather_payload(raw_weather_data, synoptic_context),
        ensure_ascii=False,
        separators=(",", ":"),
    )
    location_name = load_settings()["location_name"]
    prompt = f"""
تو یک کارشناس هواشناسی کاربردی هستی. برای {location_name} و منطقه‌ی پیرامون آن و ساحل جنوبی دریای خزر
یک تحلیل هفتگی به فارسی روان و قابل فهم برای عموم بنویس.

داده‌ی عددی مدل هواشناسی و میدان‌های سینوپتیک منطقه‌ای:
{weather_payload}

قواعد مهم:
- میدان سینوپتیک شامل فشار سطح دریا و ارتفاع ژئوپتانسیل در ۵۰۰ و ۸۵۰ هکتوپاسکال
  در چند ناحیه‌ی نمونه است؛ از آن برای مقایسه‌ی روندها استفاده کن، نه برای ادعای قطعی درباره‌ی شاخص‌ها.
- فقط بر اساس داده‌ی داده‌شده صحبت کن و اگر داده‌ای درباره‌ی شاخص‌هایی مثل NAO، پرفشار سیبری
  یا جبهه‌ی سرد اروپا وجود ندارد، ادعا نکن که آن شاخص قطعاً فعال است.
- ارتباط احتمالی الگوهای بزرگ‌مقیاس (پرفشار سیبری، NAO، جبهه‌های سرد اروپا) با هوای شمال ایران
  را با عبارت‌هایی مثل «می‌تواند» و «احتمالاً» توضیح بده، نه به‌صورت قطعیت کاذب.
- ابتدا یک جمع‌بندی کوتاه بده، سپس روند دما، بارش، باد و رطوبت را توضیح بده.
- در پایان یک بخش کوتاه «نکته‌ی کاربردی» برای مردم منطقه اضافه کن.
- پاسخ فقط فارسی، بدون جدول و حداکثر ۵ پاراگراف کوتاه باشد.
"""

    try:
        client = genai.Client(api_key=config.GEMINI_API_KEY)
        response = client.models.generate_content(
            model=config.GEMINI_MODEL,
            contents=prompt,
        )
        text = (response.text or "").strip()
        return text or Strings.ERROR_FETCHING_ANALYSIS
    except Exception as exc:
        # Do not expose the API key or raw SDK details in the UI, but give the
        # user an actionable message for the most common quota failure.
        error_text = str(exc).upper()
        if "401" in error_text or "UNAUTHENTICATED" in error_text or "INVALID API KEY" in error_text:
            return Strings.ANALYSIS_AUTH_ERROR
        if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text or "QUOTA" in error_text:
            return Strings.ANALYSIS_QUOTA_EXCEEDED
        return Strings.ERROR_FETCHING_ANALYSIS


def get_multimodel_analysis(multimodel_data: dict) -> str:
    """Compare GFS, ECMWF and ICON in one Persian Gemini response."""
    if not config.GEMINI_API_KEY:
        return Strings.ANALYSIS_NOT_CONFIGURED

    compact = {
        "location": multimodel_data.get("location"),
        "source": multimodel_data.get("source"),
        "models": multimodel_data.get("models", {}),
        "synoptic_context": multimodel_data.get("synoptic_context", {}),
    }
    payload = json.dumps(compact, ensure_ascii=False, separators=(",", ":"))
    location_name = multimodel_data.get("location") or load_settings()["location_name"]
    prompt = f"""
برای {location_name} و منطقه‌ی پیرامون آن و ساحل جنوبی دریای خزر، داده‌های سه مدل هواشناسی زیر را مقایسه کن:
GFS، ECMWF و ICON.

داده‌ی مدل‌ها و زمینه‌ی سینوپتیک:
{payload}

پاسخ را فقط به فارسی روان و با تیترهای زیر بنویس:
۱. جمع‌بندی کلی
۲. تحلیل مدل GFS
۳. تحلیل مدل ECMWF
۴. تحلیل مدل ICON
۵. توافق و اختلاف مدل‌ها
۶. جمع‌بندی کاربردی برای مردم {location_name}

قواعد:
- برای هر مدل دما، روند بارش و احتمال بارش را جداگانه توضیح بده.
- اگر مدل‌ها اختلاف دارند، دقیقاً بگو اختلاف در چیست و از قطعیت کاذب پرهیز کن.
- اگر هر سه مدل در یک روند توافق دارند، آن را به‌عنوان نقطه‌ی اطمینان بیشتر ذکر کن.
- اگر داده‌ای درباره‌ی باد، رطوبت یا شاخص‌هایی مثل NAO وجود ندارد، درباره‌ی آن حدس قطعی نزن.
- حداکثر ۸ پاراگراف کوتاه بنویس و از جدول استفاده نکن.
"""

    try:
        client = genai.Client(api_key=config.GEMINI_API_KEY)
        response = client.models.generate_content(model=config.GEMINI_MODEL, contents=prompt)
        text = (response.text or "").strip()
        return text or Strings.ERROR_FETCHING_ANALYSIS
    except Exception as exc:
        error_text = str(exc).upper()
        if "401" in error_text or "UNAUTHENTICATED" in error_text or "INVALID API KEY" in error_text:
            return Strings.ANALYSIS_AUTH_ERROR
        if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text or "QUOTA" in error_text:
            return Strings.ANALYSIS_QUOTA_EXCEEDED
        return Strings.ERROR_FETCHING_ANALYSIS



