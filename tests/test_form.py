import time

from django.test import TestCase
from wagtail.contrib.forms.models import FormSubmission
from wagtail.models import Page

from tests.testapp.models import FormField, FormPage


class TestHoneypotFormDisabled(TestCase):

    def setUp(self):
        """
        Disable honeypot on FormPage

        So nothing is blocking the form submission
        """
        # Get the site root page -> home page
        root_page = Page.objects.get(id=1)
        home_page = root_page.get_children().first()

        # Initialse a form page
        form_page = FormPage(
            title="Form Page",
            slug="formpage",
            honeypot=False,
            thank_you_text="Thank you for your message",
        )

        # Add the form page as a child of the home page
        home_page.add_child(instance=form_page)

        # Add the form fields
        FormField.objects.create(
            page=form_page, label="Name", field_type="singleline", required=True
        )
        FormField.objects.create(
            page=form_page, label="Email Address", field_type="email", required=True
        )
        FormField.objects.create(
            page=form_page, label="Message", field_type="multiline", required=True
        )

        form_page.save_revision().publish()

    def test_form_submission(self):
        """
        Test that a form submission is successful. When the honeypot is disabled
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

    def setUp(self):
        """
        Enable honeypot on FormPage

        So the form submission can be ignored when necessary
        """
        # Get the site root page -> home page
        root_page = Page.objects.get(id=1)
        home_page = root_page.get_children().first()

        # Initialse a form page
        form_page = FormPage(
            title="Form Page",
            slug="formpage",
            honeypot=True,
            thank_you_text="Thank you for your message",
        )

        # Add the form page as a child of the home page
        home_page.add_child(instance=form_page)

        # Add the form fields
        FormField.objects.create(
            page=form_page, label="Name", field_type="singleline", required=True
        )
        FormField.objects.create(
            page=form_page, label="Email Address", field_type="email", required=True
        )
        FormField.objects.create(
            page=form_page, label="Message", field_type="multiline", required=True
        )

        form_page.save_revision().publish()

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
