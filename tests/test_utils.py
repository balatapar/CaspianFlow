import unittest

from utils import format_date, format_hour, format_percentage, to_persian_digits


class UtilsTests(unittest.TestCase):
    def test_persian_digits(self):
        self.assertEqual(to_persian_digits("2026/08/10"), "۲۰۲۶/۰۸/۱۰")

    def test_date_and_hour_formatting(self):
        self.assertIn("۲۰۲۶/۰۸/۱۰", format_date("2026-08-10"))
        self.assertEqual(format_hour("2026-08-10T09:30"), "۰۹:۳۰")

    def test_percentage_formatting(self):
        self.assertEqual(format_percentage(67.4), "۶۷%")
        self.assertEqual(format_percentage(None), "—")


if __name__ == "__main__":
    unittest.main()
