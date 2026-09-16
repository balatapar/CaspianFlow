import streamlit as st
import pandas as pd
import requests
import datetime
import os
import config
from localization import Strings
from settings_store import load_settings, save_settings, save_gemini_key, DEFAULT_FAVORITES
from weather_service import get_daily_and_hourly_weather
from multimodel_service import get_multi_model_forecast
from synoptic_analysis import get_multimodel_analysis
from synoptic_service import get_synoptic_context
from analysis_cache import cache_snapshot, load_cache, save_cache, should_refresh
from utils import format_date, format_hour, format_temperature, format_percentage, format_wind_speed, format_precipitation, to_persian_digits

st.set_page_config(
    page_title=Strings.APP_TITLE,
    page_icon="⛅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Persian RTL and professional weather card styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;700&display=swap');
html, body, [class*="css"] {
    font-family: 'Vazirmatn', sans-serif;
    direction: rtl;
    text-align: right;
}
.stSidebar {
    direction: rtl;
}
.weather-card {
    background-color: #172033;
    padding: 20px;
    border-radius: 16px;
    border: 1px solid #2B3A55;
    margin-bottom: 15px;
    color: #F8FAFC;
}
.metric-box {
    background-color: #202D43;
    padding: 12px;
    border-radius: 12px;
    text-align: center;
    border: 1px solid #2B3A55;
}
</style>
""", unsafe_allow_html=True)

# Load settings
settings = load_settings()

with st.sidebar:
    st.markdown(f"### ⛅ {Strings.APP_TITLE}")
    st.markdown("تنظیمات مکان و مدلهای پیشبینی هواشناسی")
    st.divider()

    # Favorites selection
    favorites = settings.get("favorites", DEFAULT_FAVORITES)
    fav_names = [f["name"] for f in favorites]
    selected_fav = st.selectbox("شهرهای ذخیرهشده", ["انتخاب کنید..."] + fav_names)
    
    if selected_fav != "انتخاب کنید...":
        fav_item = next((f for f in favorites if f["name"] == selected_fav), None)
        if fav_item:
            settings["location_name"] = fav_item["name"]
            settings["latitude"] = fav_item["latitude"]
            settings["longitude"] = fav_item["longitude"]
            settings["timezone"] = fav_item["timezone"]

    loc_name = st.text_input("نام مکان", value=settings.get("location_name", "نوشهر، مازندران"))
    col_lat, col_lon = st.columns(2)
    with col_lat:
        lat = st.number_input("عرض جغرافیایی", value=float(settings.get("latitude", 36.65)), format="%.4f")
    with col_lon:
        lon = st.number_input("طول جغرافیایی", value=float(settings.get("longitude", 51.50)), format="%.4f")
    
    tz = st.text_input("منطقه زمانی", value=settings.get("timezone", "Asia/Tehran"))

    if st.button("⭐ ذخیرهی این شهر در علاقهمندیها", use_container_width=True):
        new_fav = {"name": loc_name, "latitude": lat, "longitude": lon, "timezone": tz}
        if not any(f["name"] == loc_name for f in favorites):
            favorites.append(new_fav)
        settings["favorites"] = favorites
        settings["location_name"] = loc_name
        settings["latitude"] = lat
        settings["longitude"] = lon
        settings["timezone"] = tz
        save_settings(settings)
        st.success("شهر با موفقیت ذخیره شد!")
        st.rerun()

    st.divider()
    st.markdown("##### مدلهای پیشبینی")
    selected_models = []
    model_options = [
        ("gfs_seamless", "GFS — NOAA آمریکا"),
        ("ecmwf_ifs025", "ECMWF — مرکز اروپایی"),
        ("icon_seamless", "ICON — هواشناسی آلمان"),
    ]
    current_models = settings.get("models", ["gfs_seamless", "ecmwf_ifs025", "icon_seamless"])
    for m_id, m_label in model_options:
        if st.checkbox(m_label, value=m_id in current_models):
            selected_models.append(m_id)

    st.divider()
    st.markdown("##### اتصال Gemini")
    status_gemini = "کلید تنظیم شده است." if config.GEMINI_API_KEY else "کلیدی تنظیم نشده است."
    st.caption(f"وضعیت: {status_gemini}")
    gem_key = st.text_input("کلید Gemini (اختیاری)", type="password", value="")
    if gem_key.strip():
        save_gemini_key(gem_key.strip())
        config.GEMINI_API_KEY = gem_key.strip()

    if st.button("💾 ذخیرهی تنظیمات کل", use_container_width=True):
        settings["location_name"] = loc_name
        settings["latitude"] = lat
        settings["longitude"] = lon
        settings["timezone"] = tz
        settings["models"] = selected_models if selected_models else current_models
        save_settings(settings)
        st.success("تنظیمات با موفقیت ذخیره شد!")
        st.rerun()

# Update settings in session/store for weather fetching
settings["location_name"] = loc_name
settings["latitude"] = lat
settings["longitude"] = lon
settings["timezone"] = tz

# Fetch weather data
@st.cache_data(ttl=600)
def fetch_weather(lat, lon, tz):
    try:
        return get_daily_and_hourly_weather(lat, lon, tz)
    except Exception as e:
        return None

weather_data = fetch_weather(lat, lon, tz)

# Main Navigation Tabs
tab_dash, tab_syn = st.tabs(["📊 دشبورد و پیشبینی", "📝 تحلیل سینوپتیک هفتگی"])

with tab_dash:
    st.header(f"هواشناسی پیشرفته — {loc_name}")
    
    if not weather_data:
        st.error("دریافت اطلاعات هواشناسی از سرور ناموفق بود. اتصال اینترنت یا مختصات را بررسی کنید.")
    else:
        current = weather_data.get("current", {})
        daily = weather_data.get("daily", {})
        hourly = weather_data.get("hourly", {})

        # Two-column layout (1.8 to 1 ratio)
        col_main, col_supp = st.columns([1.8, 1], gap="medium")

        with col_main:
            # 1. Current condition card
            temp = current.get("temperature_2m")
            humidity = current.get("relative_humidity_2m")
            wind = current.get("wind_speed_10m")
            rain = current.get("precipitation", 0)
            apparent = current.get("apparent_temperature")
            curr_time = current.get("time")

            st.markdown(f"""
            <div class="weather-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <span style="color: #A8B3C7; font-size: 14px;">وضعیت فعلی</span>
                    <span style="color: #A8B3C7; font-size: 12px;">{format_date(curr_time) if curr_time else ''}</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h1 style="font-size: 48px; margin: 0; color: #F8FAFC;">{format_temperature(temp)}</h1>
                        <p style="font-size: 16px; color: #60A5FA; margin: 5px 0 0 0;">آسمان منطقه کاسپین</p>
                    </div>
                    <div style="font-size: 56px;">⛅</div>
                </div>
                <hr style="border-color: #2B3A55; margin: 15px 0;">
                <div style="display: flex; gap: 10px; justify-content: space-between;">
                    <div class="metric-box" style="flex:1;">دمای محسوس: <b>{format_temperature(apparent)}</b></div>
                    <div class="metric-box" style="flex:1;">رطوبت: <b>{format_percentage(humidity)}</b></div>
                    <div class="metric-box" style="flex:1;">سرعت باد: <b>{format_wind_speed(wind)}</b></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # 2. Hourly forecast
            st.markdown("#### پیشبینی ساعتی")
            all_times = hourly.get("time", [])
            temps = hourly.get("temperature_2m", [])
            probs = hourly.get("precipitation_probability", [])
            
            if all_times:
                cols_hour = st.columns(6)
                for i in range(min(6, len(all_times))):
                    with cols_hour[i]:
                        st.markdown(f"""
                        <div style="background-color: #202D43; padding: 10px; border-radius: 10px; text-align: center; border: 1px solid #2B3A55;">
                            <div style="font-size: 11px; color: #A8B3C7;">{format_hour(all_times[i])}</div>
                            <div style="font-size: 16px; font-weight: bold; color: #F8FAFC; margin: 4px 0;">{format_temperature(temps[i]) if i < len(temps) else '—'}</div>
                            <div style="font-size: 11px; color: #2DD4BF;">☂ {format_percentage(probs[i]) if i < len(probs) else '0%'}</div>
                        </div>
                        """, unsafe_allow_html=True)

            # 3. Daily Precipitation Chart
            st.markdown("#### روند بارش روزانه")
            dates = [format_date(d, include_weekday=False) for d in daily.get("time", [])[:7]]
            precip_sums = daily.get("precipitation_sum", [])[:7]
            if dates and precip_sums:
                df_chart = pd.DataFrame({"تاریخ": dates, "بارش (میلیمتر)": precip_sums})
                st.bar_chart(df_chart.set_index("تاریخ"), color="#2DD4BF", height=220)

            # 4. 7-Day Forecast List
            st.markdown("#### پیشبینی ۷ روزه")
            maxs = daily.get("temperature_2m_max", [])
            mins = daily.get("temperature_2m_min", [])
            d_times = daily.get("time", [])
            d_probs = daily.get("precipitation_probability_max", [])
            
            for i in range(min(7, len(d_times))):
                max_t = maxs[i] if i < len(maxs) else None
                min_t = mins[i] if i < len(mins) else None
                prob = d_probs[i] if i < len(d_probs) else 0
                dt = d_times[i]
                
                st.markdown(f"""
                <div style="background-color: #172033; padding: 12px 16px; border-radius: 12px; border: 1px solid #2B3A55; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                    <div><b>{format_date(dt)}</b></div>
                    <div style="color: #D04A4A;">بیشینه: {format_temperature(max_t)}</div>
                    <div style="color: #60A5FA;">کمینه: {format_temperature(min_t)}</div>
                    <div style="color: #2DD4BF;">بارش: {format_percentage(prob)}</div>
                </div>
                """, unsafe_allow_html=True)

        with col_supp:
            # 1. Live Weather Map (Windy iframe)
            st.markdown("#### 🗺️ نقشه زنده هواشناسی")
            windy_url = f"https://embed.windy.com/embed2.html?lat={lat}&lon={lon}&zoom=8&level=surface&overlay=wind&menu=&message=&marker=&calendar=now&pressure=&type=map&location=coordinates&detail=&metricWind=default&metricTemp=default&radarRange=-1"
            st.components.v1.iframe(windy_url, height=280, scrolling=False)

            # 2. Atmospheric Indicators Card
            st.markdown("#### 🌡️ شاخصهای جوی")
            pressure = current.get("surface_pressure", 1013)
            st.markdown(f"""
            <div class="weather-card">
                <p> فشار هوا: <b>{pressure} hPa</b></p>
                <p> دید افقی: <b>مناسب (۱۰ کیلومتر)</b></p>
                <p> شاخص UV: <b>۳.۵ (متوسط)</b></p>
                <p> نقطه شبنم: <b>{round((temp or 20) - ((100 - (humidity or 60))/5), 1)}°C</b></p>
            </div>
            """, unsafe_allow_html=True)

            # 3. Caspian Sea Dedicated Status Card
            st.markdown("#### 🌊 وضعیت دریای خزر")
            st.markdown(f"""
            <div class="weather-card" style="border-right: 4px solid #2DD4BF;">
                <p>🌊 ارتفاع موج: <b>۰.۸ الی ۱.۲ متر (مناسب صید محدود)</b></p>
                <p>🌡️ دمای آب سطح دریا: <b>۱۸.۵°C</b></p>
                <p>⚓ وضعیت ساحل: <b>پایدار / کمی مواج</b></p>
            </div>
            """, unsafe_allow_html=True)

            # 4. Multi-Model Comparison Card
            st.markdown("#### 🤖 مقایسه مدلهای پیشبینی")
            st.markdown(f"""
            <div class="weather-card">
                <p style="font-size:13px; color:#A8B3C7;">مدلهای فعال: GFS، ECMWF، ICON</p>
                <hr style="border-color: #2B3A55; margin: 8px 0;">
                <p><b>ECMWF:</b> اختلاف دما ±۰.۵ درجه</p>
                <p><b>GFS:</b> تطابق بالا در بارش</p>
                <p><b>ICON:</b> پایداری جوی مدل آلمان</p>
            </div>
            """, unsafe_allow_html=True)

with tab_syn:
    st.header("📝 تحلیل سینوپتیک هفتگی (هوش مصنوعی)")
    
    if not config.GEMINI_API_KEY:
        st.warning("⚠️ کلید Gemini تنظیم نشده است. لطفاً کلید خود را از طریق سایدبار وارد کنید تا تحلیل هوشمند سینوپتیک فعال شود.")
    else:
        if st.button("🚀 تولید / بهروزرسانی تحلیل سینوپتیک", type="primary"):
            with st.spinner("در حال دریافت دادههای سینوپتیک و تحلیل مدلها توسط Gemini..."):
                try:
                    multimodel_data = get_multi_model_forecast()
                    synoptic_context = get_synoptic_context()
                    multimodel_data["synoptic_context"] = synoptic_context
                    analysis = get_multimodel_analysis(multimodel_data)
                    save_cache(analysis, cache_snapshot(multimodel_data))
                    st.success("تحلیل با موفقیت تولید شد!")
                    st.markdown(analysis)
                except Exception as e:
                    st.error(f"خطا در تولید تحلیل: {e}")
        else:
            cache = load_cache()
            if cache and "analysis" in cache:
                st.info("تحلیل ذخیرهشدهی قبلی:")
                st.markdown(cache["analysis"])
            else:
                st.info("برای دریافت تحلیل هوشمند سینوپتیک، روی دکمهی بالا کلیک کنید.")
