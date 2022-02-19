from django.conf import settings
from django.db import models
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
        if honeypot_name in form.data and not form.data[honeypot_name]:
            return super().process_form_submission(form)
