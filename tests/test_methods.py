import time

from django.test import TestCase

from tests.testapp.models import FormPage


class TestHoneypotMethods(TestCase):
    """
    Test the methods used in the honeypot form to generate a timestamp
    """

    def setUp(self):
        self.interval = 3  # seconds
        self.form = FormPage()
        self.form_render_time = int(str(time.time()).split(".")[0])

    def test_instant_submit(self):
        self.assertFalse(self.form.time_diff(self.form_render_time, self.interval))

    def test_delayed_submit_interval(self):
        self.assertFalse(self.form.time_diff(self.form_render_time - 3, self.interval))

    def test_delayed_submit_long_interval(self):
        self.assertTrue(self.form.time_diff(self.form_render_time - 4, self.interval))

    def test_delayed_submit_longer_interval(self):
        self.assertTrue(self.form.time_diff(self.form_render_time - 10, self.interval))
