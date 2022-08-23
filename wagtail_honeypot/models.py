import time

from django.conf import settings
from django.db import models
from wagtail import VERSION as WAGTAIL_VERSION

if WAGTAIL_VERSION > (3, 0):
    from wagtail.admin.panels import FieldPanel, MultiFieldPanel
else:
    from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel

from wagtail.contrib.forms.models import AbstractEmailForm


class HoneypotMixin(AbstractEmailForm):
    honeypot = models.BooleanField(default=False, verbose_name="Honeypot Enabled")

    honeypot_panels = [
        MultiFieldPanel(
            [
                FieldPanel("honeypot"),
            ],
            heading="Reduce Form Spam",
        )
    ]

    class Meta:
        abstract = True

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
