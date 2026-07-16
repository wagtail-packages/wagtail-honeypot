from unittest.mock import patch

from django.test import TestCase

from tests.testapp.models import FormPage


class TestHoneypotMethods(TestCase):
    """
    Test the methods used in the honeypot form to generate a timestamp
    """

    def setUp(self):
        self.interval = 3  # seconds
        self.form = FormPage()
        self.current_time = 1_700_000_000
        self.form_render_time = self.current_time

    @patch("wagtail_honeypot.models.time.time")
    def test_time_diff_thresholds(self, mock_time):
        mock_time.return_value = self.current_time
        cases = [
            ("instant submit", self.form_render_time, False),
            ("equal to interval", self.form_render_time - self.interval, False),
            ("greater than interval", self.form_render_time - (self.interval + 1), True),
            ("much greater than interval", self.form_render_time - 10, True),
        ]

        for label, submitted_time, expected in cases:
            with self.subTest(label=label):
                self.assertEqual(self.form.time_diff(submitted_time, self.interval), expected)

    def test_time_diff_rejects_invalid_values(self):
        cases = [
            ("empty string", ""),
            ("non-numeric string", "not-a-timestamp"),
            ("none", None),
        ]

        for label, submitted_time in cases:
            with self.subTest(label=label):
                self.assertFalse(self.form.time_diff(submitted_time, self.interval))
