from bs4 import BeautifulSoup as bs4
from django.template import Context, Template
from django.test import TestCase, override_settings

from wagtail_honeypot.templatetags.honeypot_tags import honeypot_fields


class TestHoneypotTemplateTags(TestCase):
    """
    Test the honeypot template tags
    """

    def test_honeypot_template_tag_context_enabled(self):
        """
        Test that the honeypot template tag returns the correct data
        when the honeypot is enabled
        """
        fields_data = honeypot_fields(True)
        self.assertEqual(fields_data["honeypot_name_field"], "whf_name")
        self.assertEqual(fields_data["honeypot_time_field"], "whf_time")
        self.assertIsInstance(int(fields_data["time"]), int)
        self.assertTrue(fields_data["enabled"])

    def test_honeypot_template_tag_context_disabled(self):
        """
        Test that the honeypot template tag returns the correct data
        when the honeypot is disabled
        """
        fields_data = honeypot_fields(False)
        self.assertFalse(fields_data["enabled"])

    def test_honeypot_tags_rendered(self):
        """
        Test that the honeypot template tag renders the correct HTML
        when the honeypot is enabled
        """
        context = Context({"honeypot": True})
        template = Template("{% load honeypot_tags %}{% honeypot_fields honeypot %}")

        soup = bs4(template.render(context), "html.parser")

        input_text = soup.find(
            "input", {"id": "whf_name", "name": "whf_name", "type": "text"}
        )
        self.assertIsNotNone(input_text)

        input_time = soup.find(
            "input", {"id": "whf_time", "name": "whf_time", "type": "hidden"}
        )
        self.assertIsNotNone(input_time)

    @override_settings(HONEYPOT_NAME_FIELD="foo", HONEYPOT_TIME_FIELD="bar")
    def test_honeypot_tags_override_field_names(self):
        """
        Test that the honeypot template tag renders the correct HTML
        when the honeypot is enabled and the field names are overridden
        """
        context = Context({"honeypot": True})
        template = Template("{% load honeypot_tags %}{% honeypot_fields honeypot %}")

        soup = bs4(template.render(context), "html.parser")

        input_text = soup.find("input", {"id": "foo", "name": "foo", "type": "text"})
        self.assertIsNotNone(input_text)

        input_time = soup.find("input", {"id": "bar", "name": "bar", "type": "hidden"})
        self.assertIsNotNone(input_time)
