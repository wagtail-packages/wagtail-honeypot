from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    TabbedInterface,
)
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.fields import RichTextField

from wagtail_honeypot.models import HoneypotMixin


class FormField(AbstractFormField):
    page = ParentalKey("FormPage", on_delete=models.CASCADE, related_name="form_fields")


class FormPage(HoneypotMixin):
    """FormPage should inherit from HoneypotMixin"""

    intro = RichTextField(blank=True)
    thank_you_text = RichTextField(blank=True)

    content_panels = AbstractEmailForm.content_panels + [
        FieldPanel("intro"),
        InlinePanel("form_fields", label="Form fields"),
        FieldPanel("thank_you_text"),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("from_address", classname="col6"),
                        FieldPanel("to_address", classname="col6"),
                    ]
                ),
                FieldPanel("subject"),
            ],
            "Email",
        ),
    ]

    """add a edit_handler to enable the Honeypot tab"""
    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(HoneypotMixin.honeypot_panels, heading="Honeypot"),
            ObjectList(HoneypotMixin.promote_panels, heading="Promote"),
            ObjectList(
                HoneypotMixin.settings_panels, heading="Settings", classname="settings"
            ),
        ]
    )

    """OR add a the honeypot checkbox without the extra tab"""
    # content_panels = content_panels + HoneypotMixin.honeypot_panels
