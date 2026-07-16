import time

from django.test import TestCase
from wagtail.contrib.forms.models import FormSubmission
from wagtail.models import Page

from tests.testapp.models import FormField, FormPage


class HoneypotFormPageTestCase(TestCase):
    def create_form_page(self, *, honeypot):
        # Get the site root page -> home page
        root_page = Page.objects.get(id=1)
        home_page = root_page.get_children().first()

        form_page = FormPage(
            title="Form Page",
            slug="formpage",
            honeypot=honeypot,
            thank_you_text="Thank you for your message",
        )

        home_page.add_child(instance=form_page)

        FormField.objects.create(page=form_page, label="Name", field_type="singleline", required=True)
        FormField.objects.create(page=form_page, label="Email Address", field_type="email", required=True)
        FormField.objects.create(page=form_page, label="Message", field_type="multiline", required=True)

        form_page.save_revision().publish()
        return form_page

    def post_form(self, **overrides):
        payload = {
            "name": "foo",
            "email_address": "foo@foo.com",
            "message": "foo",
            "whf_name": "",
            "whf_time": self.form_view_time,
        }
        payload.update(overrides)
        for key, value in tuple(payload.items()):
            if value is self.remove_field:
                payload.pop(key)
        return self.client.post("/formpage/", payload)


class TestHoneypotFormDisabled(HoneypotFormPageTestCase):
    def setUp(self):
        """
        Disable honeypot on FormPage

        So nothing is blocking the form submission
        """
        self.create_form_page(honeypot=False)
        self.form_view_time = 123456789
        self.remove_field = object()

    def test_form_submission_succeeds_when_honeypot_disabled(self):
        """
        Test that a form submission is successful. When the honeypot is disabled
        """
        resp = self.post_form()
        self.assertEqual(FormSubmission.objects.count(), 1)
        self.assertContains(resp, "Thank you for your message")


class TestHoneypotFormEnabled(HoneypotFormPageTestCase):
    def setUp(self):
        """
        Enable honeypot on FormPage

        So the form submission can be ignored when necessary
        """
        self.create_form_page(honeypot=True)
        self.form_view_time = int(str(time.time()).split(".")[0])
        self.remove_field = object()

    def assert_submission_count(self, expected_count):
        self.assertEqual(FormSubmission.objects.count(), expected_count)

    def test_form_submission_succeeds_with_valid_honeypot_values(self):
        """
        Test that a form submission is successful

        When the honeypot is enabled and the time to submit the form
        is longer than the interval set in the settings and no text
        is entered in the honeypot field
        """
        resp = self.post_form(whf_time=self.form_view_time - 10)
        self.assert_submission_count(1)
        self.assertContains(resp, "Thank you for your message")

    def test_form_submission_is_ignored_when_honeypot_time_is_too_short(self):
        """
        Test that a form submission is unsuccessful

        When the honeypot is enabled and the time to submit the form
        is shorter than the interval set in the settings and no text
        is entered in the honeypot field
        """
        resp = self.post_form(whf_time=self.form_view_time - 1)
        self.assert_submission_count(0)
        self.assertContains(resp, "Thank you for your message")

    def test_form_submission_is_ignored_when_honeypot_time_is_invalid(self):
        for value in ("", "not-a-timestamp"):
            with self.subTest(value=value):
                resp = self.post_form(whf_time=value)
                self.assert_submission_count(0)
                self.assertContains(resp, "Thank you for your message")

    def test_form_submission_is_ignored_when_honeypot_text_is_filled(self):
        """
        Test that a form submission is unsuccessful

        When the honeypot is enabled and the time to submit the form
        is longer than the interval set in the settings and text
        is entered in the honeypot field
        """
        resp = self.post_form(whf_name="foo", whf_time=self.form_view_time - 10)
        self.assert_submission_count(0)
        self.assertContains(resp, "Thank you for your message")

    def test_form_submission_is_ignored_when_honeypot_name_field_is_missing(self):
        resp = self.post_form(whf_name=self.remove_field, whf_time=self.form_view_time - 10)
        self.assert_submission_count(0)
        self.assertContains(resp, "Thank you for your message")

    def test_form_submission_is_ignored_when_honeypot_time_field_is_missing(self):
        resp = self.post_form(whf_time=self.remove_field)
        self.assert_submission_count(0)
        self.assertContains(resp, "Thank you for your message")

    def test_form_submission_is_ignored_when_both_honeypot_fields_are_missing(self):
        resp = self.post_form(whf_name=self.remove_field, whf_time=self.remove_field)
        self.assert_submission_count(0)
        self.assertContains(resp, "Thank you for your message")
