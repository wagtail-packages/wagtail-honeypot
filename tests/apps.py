from django.apps import AppConfig


class WagtailHoneypotTestAppConfig(AppConfig):
    label = "tests"
    name = "tests"
    verbose_name = "Wagtail Honeypot tests"

    default_auto_field = "django.db.models.AutoField"
