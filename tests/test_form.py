import time

from django.test import TestCase
from wagtail.contrib.forms.models import FormSubmission

from tests.testapp.models import FormPage


class TestHoneypotFormDisabled(TestCase):
    fixtures = ["dump.json"]

    def setUp(self):
        """
        Disable honeypot on FormPage

        So nothing is blocking the form submission
        """
        form_page = FormPage.objects.get(slug="formpage")
        form_page.honeypot = False
        form_page.save()

    def test_form_submission(self):
        """
        Test that a form submission is successful

        When the honeypot is disabled
        """
        resp = self.client.post(
            "/formpage/",
            {
                "name": "foo",
                "email_address": "foo@foo.com",
                "message": "foo",
                "whf_name": "",
                "whf_time": 123456789,
            },
        )
        submissions_count = FormSubmission.objects.all().count()
        self.assertEqual(submissions_count, 1)
        self.assertContains(resp, "Thank you for your message")


class TestHoneypotFormEnabled(TestCase):
    fixtures = ["dump.json"]

    def setUp(self):
        """
        Enable honeypot on FormPage

        So the form submission can be ignored when necessary
        """
        form_page = FormPage.objects.get(slug="formpage")
        form_page.honeypot = True
        form_page.save()
        self.form_view_time = int(str(time.time()).split(".")[0])

    def test_form_submission(self):
        """
        Test that a form submission is successful

        When the honeypot is enabled and the time to submit the form
        is longer than the interval set in the settings and no text
        is entered in the honeypot field
        """
        resp = self.client.post(
            "/formpage/",
            {
                "name": "foo",
                "email_address": "foo@foo.com",
                "message": "foo",
                "whf_name": "",  # no text in the honeypot field
                "whf_time": self.form_view_time - 10,  # a time in the past
            },
        )
        submissions_count = FormSubmission.objects.all().count()
        self.assertEqual(submissions_count, 1)
        self.assertContains(resp, "Thank you for your message")

    def test_form_submission_honeypot_time(self):
        """
        Test that a form submission is successful

        When the honeypot is enabled and the time to submit the form
        is shorter than the interval set in the settings and no text
        is entered in the honeypot field
        """
        resp = self.client.post(
            "/formpage/",
            {
                "name": "foo",
                "email_address": "foo@foo.com",
                "message": "foo",
                "whf_name": "",  # no text in the honeypot field
                "whf_time": self.form_view_time - 1,  # only q second difference
            },
        )
        submissions_count = FormSubmission.objects.all().count()
        self.assertEqual(submissions_count, 0)
        self.assertContains(resp, "Thank you for your message")

    def test_form_submission_honeypot_text_filled(self):
        """
        Test that a form submission is unsuccessful

        When the honeypot is enabled and the time to submit the form
        is longer than the interval set in the settings and text
        is entered in the honeypot field
        """
        resp = self.client.post(
            "/formpage/",
            {
                "name": "foo",
                "email_address": "foo@foo.com",
                "message": "foo",
                "whf_name": "foo",  # text in the honeypot field
                "whf_time": self.form_view_time - 10,  # A time in the past
            },
        )
        submissions_count = FormSubmission.objects.all().count()
        self.assertEqual(submissions_count, 0)
        self.assertContains(resp, "Thank you for your message")
