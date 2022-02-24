import time

from bs4 import BeautifulSoup as bs4
from django.template import Context, Template
from django.test import TestCase, override_settings
from wagtail.contrib.forms.models import FormSubmission

from wagtail_honeypot.templatetags.honeypot_tags import honeypot_fields
from wagtail_honeypot.test.models import FormPage


class TestHoneypotResponses(TestCase):
    fixtures = ["initialdata.json"]

    def setUp(self):
        self.resp = self.client.get("/form-page/")

    def test_form_page(self):
        resp = self.resp
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "<h1>Form Page</h1>")
        self.assertContains(resp, "<form")
        self.assertContains(resp, 'action="/form-page/"')
        self.assertContains(resp, 'method="POST"')
        self.assertContains(resp, '<input type="text" name="whf_name" id="whf_name"')
        self.assertContains(resp, '<input type="hidden" name="whf_time"')
        self.assertContains(resp, '<input type="text" name="name"')
        self.assertContains(resp, '<input type="email" name="email_address"')
        self.assertContains(resp, '<textarea name="message"')
        self.assertContains(resp, '<input type="submit"')


class TestHoneypotMethods(TestCase):
    def setUp(self):
        self.interval = 3  # seconds
        self.form = FormPage()
        self.form_render_time = int(str(time.time()).split(".")[0])

    def test_time_diff_instant_submit(self):
        self.assertFalse(self.form.time_diff(self.form_render_time, self.interval))

    def test_time_diff_delayed_submit_is_interval(self):
        self.assertFalse(self.form.time_diff(self.form_render_time - 3, self.interval))

    def test_time_diff_delayed_submit_long_intreval(self):
        self.assertTrue(self.form.time_diff(self.form_render_time - 4, self.interval))

    def test_time_diff_delayed_submit_longer_intreval(self):
        self.assertTrue(self.form.time_diff(self.form_render_time - 10, self.interval))


class TestHoneypotTemplateTags(TestCase):
    def test_honeypot_template_tag_context(self):
        fields_data = honeypot_fields()
        self.assertEqual(fields_data["honeypot_name"], "whf_name")
        self.assertEqual(fields_data["honeypot_time"], "whf_time")
        self.assertIsInstance(int(fields_data["time"]), int)

    @override_settings(HONEYPOT_NAME_FIELD="foo", HONEYPOT_TIME_FIELD="bar")
    def test_honeypot_tags_rendered(self):
        context = Context({})
        template = Template("{% load honeypot_tags %}{% honeypot_fields %}")

        soup = bs4(template.render(context), "html.parser")

        input_text = soup.find("input", {"id": "foo", "name": "foo", "type": "text"})
        self.assertIsNotNone(input_text)

        input_time = soup.find("input", {"id": "bar", "name": "bar", "type": "hidden"})
        self.assertIsNotNone(input_time)


class TestHoneypotFormDisabled(TestCase):
    fixtures = ["initialdata.json"]

    def setUp(self):
        form_page = FormPage.objects.get(slug="form-page")
        form_page.honeypot = False
        form_page.save()

    def test_form_submission(self):
        resp = self.client.post(
            "/form-page/",
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

    def test_form_submission_from_bot(self):
        resp = self.client.post(
            "/form-page/",
            {
                "name": "foo",
                "email_address": "foo@foo.com",
                "message": "foo",
                "whf_name": "im a bot but i won't get caught",
                "whf_time": 123456789,
            },
        )
        submissions_count = FormSubmission.objects.all().count()
        self.assertEqual(submissions_count, 1)
        self.assertContains(resp, "Thank you for your message")


class TestHoneypotFormEnabled(TestCase):
    fixtures = ["initialdata.json"]

    def setUp(self):
        form_page = FormPage.objects.get(slug="form-page")
        form_page.honeypot = True
        form_page.save()
        self.form_view_time = int(str(time.time()).split(".")[0])

    def test_form_submission(self):
        resp = self.client.post(
            "/form-page/",
            {
                "name": "foo",
                "email_address": "foo@foo.com",
                "message": "foo",
                "whf_name": "",
                "whf_time": self.form_view_time - 10,
            },
        )
        submissions_count = FormSubmission.objects.all().count()
        self.assertEqual(submissions_count, 1)
        self.assertContains(resp, "Thank you for your message")

    def test_form_submission_honeypot_text_filled(self):
        resp = self.client.post(
            "/form-page/",
            {
                "name": "foo",
                "email_address": "foo@foo.com",
                "message": "foo",
                "whf_name": "foo",
                "whf_time": self.form_view_time - 10,
            },
        )
        submissions_count = FormSubmission.objects.all().count()
        self.assertEqual(submissions_count, 0)
        self.assertContains(resp, "Thank you for your message")

    def test_form_submission_honeypot_time_low(self):
        resp = self.client.post(
            "/form-page/",
            {
                "name": "foo",
                "email_address": "foo@foo.com",
                "message": "foo",
                "whf_name": "",
                "whf_time": self.form_view_time - 1,
            },
        )
        submissions_count = FormSubmission.objects.all().count()
        self.assertEqual(submissions_count, 0)
        self.assertContains(resp, "Thank you for your message")
