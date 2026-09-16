import unittest
from unittest.mock import Mock, patch

from multimodel_service import WEATHER_MODELS, get_multi_model_forecast


class MultiModelServiceTests(unittest.TestCase):
    def test_splits_model_suffixes(self):
        daily = {"time": ["2026-08-10"], "temperature_2m_max_gfs_seamless": [30], "temperature_2m_min_gfs_seamless": [22], "precipitation_sum_gfs_seamless": [2], "precipitation_probability_max_gfs_seamless": [60], "temperature_2m_max_ecmwf_ifs025": [29], "temperature_2m_min_ecmwf_ifs025": [21], "precipitation_sum_ecmwf_ifs025": [3], "precipitation_probability_max_ecmwf_ifs025": [70], "temperature_2m_max_icon_seamless": [31], "temperature_2m_min_icon_seamless": [23], "precipitation_sum_icon_seamless": [1], "precipitation_probability_max_icon_seamless": [50]}
        hourly = {"time": ["2026-08-10T00:00"], "temperature_2m_gfs_seamless": [24], "temperature_2m_ecmwf_ifs025": [23], "temperature_2m_icon_seamless": [25], "precipitation_probability_gfs_seamless": [40], "precipitation_probability_ecmwf_ifs025": [50], "precipitation_probability_icon_seamless": [30], "pressure_msl_gfs_seamless": [1005], "pressure_msl_ecmwf_ifs025": [1006], "pressure_msl_icon_seamless": [1004]}
        response = Mock()
        response.json.return_value = {"timezone": "Asia/Tehran", "daily": daily, "hourly": hourly}
        response.raise_for_status.return_value = None

        with patch("multimodel_service.requests.get", return_value=response):
            result = get_multi_model_forecast()

        self.assertEqual(set(result["models"]), set(WEATHER_MODELS))
        self.assertEqual(result["models"]["ecmwf_ifs025"]["daily"]["temperature_max"], [29])
        self.assertEqual(result["models"]["icon_seamless"]["hourly"]["pressure_msl"], [1004])


if __name__ == "__main__":
    unittest.main()
