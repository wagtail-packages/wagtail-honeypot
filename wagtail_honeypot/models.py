import time

from django.conf import settings
from django.db import models
from wagtail.contrib.forms.models import AbstractEmailForm


class HoneypotFormMixin(models.Model):
    """
    Model to provide the honeypot field
    """

    honeypot = models.BooleanField(default=False, verbose_name="Honeypot Enabled")

    class Meta:
        abstract = True


class HoneypotFormSubmissionMixin(AbstractEmailForm):
    """
    Adds the overridden process_form_submission method to your form model
    """

    def process_form_submission(self, form):
        honeypot_name = getattr(settings, "HONEYPOT_NAME", "whf_name")
        honeypot_time = getattr(settings, "HONEYPOT_TIME", "whf_time")
        honeypot_interval = getattr(settings, "HONEYPOT_INTERVAL", 3)

        # honey pot disabled
        if not self.honeypot:
            return super().process_form_submission(form)

        # honeypot enabled
        score = []
        if honeypot_name in form.data and honeypot_time in form.data:
            score.append(form.data[honeypot_name] == "")
            score.append(self.time_diff(form.data[honeypot_time], honeypot_interval))
            return (
                super().process_form_submission(form)
                if len(score) and all(score)
                else None
            )

    @staticmethod
    def time_diff(value, interval):
        now_time = str(time.time()).split(".")[0]
        diff = abs(int(now_time) - int(value))
        return True if diff > interval else False

    class Meta:
        abstract = True
