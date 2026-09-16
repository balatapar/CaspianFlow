import unittest
from unittest.mock import Mock, patch

from synoptic_service import SYNOPTIC_POINTS, get_synoptic_context


class SynopticServiceTests(unittest.TestCase):
    def test_fetches_all_synoptic_regions(self):
        hourly = {
            "time": [f"2026-08-10T{hour:02d}:00" for hour in range(48)],
            "pressure_msl": [1000 + hour * 0.1 for hour in range(48)],
            "geopotential_height_500hPa": [5500 + hour for hour in range(48)],
            "geopotential_height_850hPa": [1500 + hour * 0.2 for hour in range(48)],
        }
        response = Mock()
        response.json.return_value = [
            {"timezone": "UTC", "hourly": hourly} for _ in SYNOPTIC_POINTS
        ]
        response.raise_for_status.return_value = None

        with patch("synoptic_service.requests.get", return_value=response) as get:
            context = get_synoptic_context()

        self.assertEqual(len(context["regions"]), len(SYNOPTIC_POINTS))
        self.assertEqual(context["regions"][0]["pressure_msl_hpa"]["first"], 1000.0)
        get.assert_called_once()
        self.assertIn("geopotential_height_500hPa", get.call_args.kwargs["params"]["hourly"])


if __name__ == "__main__":
    unittest.main()
