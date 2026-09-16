import unittest
from datetime import datetime, timedelta, timezone

from analysis_cache import cache_snapshot, should_refresh


class AnalysisCacheTests(unittest.TestCase):
    def setUp(self):
        self.forecast = {
            "models": {
                "gfs": {"daily": {"temperature_max": [30, 31, 32], "temperature_min": [22, 23, 24], "precipitation_sum": [1, 0, 2], "precipitation_probability": [20, 10, 30]}}
            }
        }

    def test_fresh_cache_does_not_refresh(self):
        cache = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "analysis": "cached",
            "forecast_snapshot": cache_snapshot(self.forecast),
        }
        self.assertFalse(should_refresh(cache, self.forecast))

    def test_force_refresh(self):
        cache = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "analysis": "cached",
            "forecast_snapshot": cache_snapshot(self.forecast),
        }
        self.assertTrue(should_refresh(cache, self.forecast, force=True))

    def test_significant_change_refreshes_after_cooldown(self):
        old = {"models": {"gfs": {"daily": {"temperature_max": [25, 26, 27], "temperature_min": [18, 19, 20], "precipitation_sum": [1, 0, 2], "precipitation_probability": [20, 10, 30]}}}}
        cache = {
            "generated_at": (datetime.now(timezone.utc) - timedelta(hours=7)).isoformat(),
            "analysis": "cached",
            "forecast_snapshot": cache_snapshot(old),
        }
        self.assertTrue(should_refresh(cache, self.forecast))


if __name__ == "__main__":
    unittest.main()
