from django.template import Context, Template
from django.test import TestCase, override_settings
from wagtail.contrib.forms.models import FormSubmission

from wagtail_honeypot.templatetags.honeypot_tags import honeypot_field


class TestWagtailHoneypotResponses(TestCase):
    fixtures = ["initialdata.json"]

    def test_form_page(self):
        home_page = self.client.get("/form-page/")
        self.assertEqual(home_page.status_code, 200)

    def test_form_page_has_heading(self):
        resp = self.client.get("/form-page/")
        self.assertContains(resp, "<h1>Form Page</h1>")

    def test_form_page_has_form(self):
        resp = self.client.get("/form-page/")
        self.assertContains(resp, "<form")

    def test_form_page_has_honeypot(self):
        resp = self.client.get("/form-page/")
        self.assertContains(resp, '<input type="text" name="whf_name" id="whf_name"')

    def test_form_page_has_submit_button(self):
        resp = self.client.get("/form-page/")
        self.assertContains(resp, '<input type="submit"')

    def test_form_page_has_form_action(self):
        resp = self.client.get("/form-page/")
        self.assertContains(resp, 'action="/form-page/"')

    def test_form_page_has_form_method(self):
        resp = self.client.get("/form-page/")
        self.assertContains(resp, 'method="POST"')

    def test_form_page_has_name_field(self):
        resp = self.client.get("/form-page/")
        self.assertContains(resp, '<input type="text" name="name"')

    def test_form_page_has_email_field(self):
        resp = self.client.get("/form-page/")
        self.assertContains(resp, '<input type="email" name="email_address"')

    def test_form_page_has_message_field(self):
        resp = self.client.get("/form-page/")
        self.assertContains(resp, '<textarea name="message"')


class TestWagtailHoneypotTemplateTags(TestCase):
    def test_honeypot_tags(self):
        self.assertEqual(
            honeypot_field(),
            {
                "honeypot_name": "whf_name",
            },
        )

    @override_settings(HONEYPOT_NAME="foo")
    def test_honeypot_tags_rendered(self):
        context = Context({})
        template = Template("{% load honeypot_tags %}{% honeypot_field %}")
        rendered_template = template.render(context)
        self.assertInHTML(
            '<input type="text" name="foo" id="foo" data-foo tabindex="-1" autocomplete="off">',
            rendered_template,
        )


class TestWagtailHoneypotForm(TestCase):
    fixtures = ["initialdata.json"]

    def test_form_page_not_bot(self):
        resp = self.client.post(
            "/form-page/",
            {
                "name": "foo",
                "email_address": "foo@foo.com",
                "message": "foo",
                "whf_name": "",
            },
        )
        submissions_count = FormSubmission.objects.all().count()
        self.assertEqual(submissions_count, 1)
        self.assertContains(resp, "Thank you for your message")

    def test_form_page_is_bot(self):
        resp = self.client.post(
            "/form-page/",
            {
                "name": "foo",
                "email_address": "foo@foo.com",
                "message": "foo",
                "whf_name": "foo",
            },
        )
        submissions_count = FormSubmission.objects.all().count()
        self.assertEqual(submissions_count, 0)
        self.assertContains(resp, "Thank you for your message")
