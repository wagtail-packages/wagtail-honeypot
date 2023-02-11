import time

from django import template
from django.conf import settings
from django.utils.text import slugify

register = template.Library()


@register.inclusion_tag("tags/honeypot_fields.html")
def honeypot_fields(enabled):
    return {
        "honeypot_name_field": slugify(
            getattr(settings, "HONEYPOT_NAME_FIELD", "whf_name")
        ),
        "honeypot_time_field": slugify(
            getattr(settings, "HONEYPOT_TIME_FIELD", "whf_time")
        ),
        "time": str(time.time()).split(".")[0],
        "enabled": enabled,
    }
