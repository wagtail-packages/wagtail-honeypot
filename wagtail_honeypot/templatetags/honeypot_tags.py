from django import template
from django.conf import settings
from django.utils.text import slugify

register = template.Library()


@register.inclusion_tag("tags/honeypot_field.html")
def honeypot_field():
    return {
        "honeypot_name": slugify(getattr(settings, "HONEYPOT_NAME", "whf_name")),
    }
