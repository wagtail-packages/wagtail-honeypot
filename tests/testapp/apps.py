from django.apps import AppConfig


class WagtailHoneypotTestAppConfig(AppConfig):
    label = "tests_testapp"
    name = "tests.testapp"
    verbose_name = "Wagtail Honeypot test app"

    default_auto_field = "django.db.models.AutoField"
