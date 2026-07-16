import time

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.contrib.forms.models import AbstractEmailForm


def get_honeypot_default():
    return getattr(settings, "HONEYPOT_ENABLED_DEFAULT", False)


class HoneypotFormMixin(models.Model):
    """
    Model to provide the honeypot field
    """

    honeypot = models.BooleanField(default=get_honeypot_default, verbose_name=_("Honeypot enabled"))

    class Meta:
        abstract = True


class HoneypotFormSubmissionMixin(AbstractEmailForm):
    """
    Adds the overridden process_form_submission method to your form model
    """

    def process_form_submission(self, form):
        honeypot_name_field = getattr(settings, "HONEYPOT_NAME_FIELD", "whf_name")
        honeypot_time_field = getattr(settings, "HONEYPOT_TIME_FIELD", "whf_time")
        honeypot_time_interval = getattr(settings, "HONEYPOT_TIME_INTERVAL", 3)

        # honey pot disabled
        if not self.honeypot:
            return super().process_form_submission(form)

        # honeypot enabled
        if honeypot_name_field in form.data and honeypot_time_field in form.data:
            is_empty = form.data[honeypot_name_field] == ""
            is_delayed = self.time_diff(form.data[honeypot_time_field], honeypot_time_interval)
            return super().process_form_submission(form) if is_empty and is_delayed else None

    @staticmethod
    def time_diff(value, interval):
        now_time = str(time.time()).split(".")[0]
        try:
            submitted_time = int(value)
        except (TypeError, ValueError):
            return False
        diff = abs(int(now_time) - submitted_time)
        return True if diff > interval else False

    class Meta:
        abstract = True
