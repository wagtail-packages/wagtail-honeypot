# Wagtail Honeypot

![Alt text](docs/sample.jpg?raw=true "Title")

## Add optional form spam protection to your Wagtail forms

It should help to reduce form spam by tricking bots into submitting data in fields that should remain empty.

### How it works

When the Wagtail Form is submitted and the honeypot protection is enabled, the honeypot fields & values are available in the `POST` data.

It provides validation for a hidden text field that should remain empty and checks a time interval between the form being displayed and submitted.

If the form is submitted with content in the hidden field or before the interval expires the submission is ignored.

- No email is sent
- No submission is stored

## Installation and setup

Add the package to your python environment.

```bash
pip install wagtail-honeypot
```

Add the package to your settings

```python
INSTALLED_APPS = [
    ...
    "wagtail_honeypot",
    ...
]
```

### The HoneypotFormMixin & HoneypotFormSubmissionMixin

They will add a [honeypot enable/disable](./wagtail_honeypot/models.py#L13) field to your form page model and [custom form submission](./wagtail_honeypot/models.py#L24) method.

If you follow the official Wagtail docs for the [Form Builder](https://docs.wagtail.org/en/stable/reference/contrib/forms/index.html) your form should look something like this...

```python
from wagtail_honeypot.models import (
    HoneypotFormMixin, HoneypotFormSubmissionMixin
)

class FormField(AbstractFormField):
    page = ParentalKey("FormPage", related_name="form_fields")

class FormPage(HoneypotFormMixin, HoneypotFormSubmissionMixin):
    intro = RichTextField(blank=True)
    thank_you_text = RichTextField(blank=True)

    content_panels = AbstractEmailForm.content_panels + [
        FieldPanel("intro", classname="full"),
        InlinePanel("form_fields", label="Form fields"),
        FieldPanel("thank_you_text", classname="full"),
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

    honeypot_panels = [
        MultiFieldPanel(
            [FieldPanel("honeypot")],
            heading="Reduce Form Spam",
        )
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(honeypot_panels, heading="Honeypot"),
            ObjectList(Page.promote_panels, heading="Promote"),
            ObjectList(Page.settings_panels, heading="Settings", classname="settings"),
        ]
    )
```

If you prefer you could add the honeypot field to the content_panels rather than a new Tab

```python
# replace
edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(honeypot_panels, heading="Honeypot"),
            ObjectList(Page.promote_panels, heading="Promote"),
            ObjectList(Page.settings_panels, heading="Settings", classname="settings"),
        ]
    )

# with
content_panels = content_panels + honeypot_panels
```

*Run `python manage.py makemigrations` and `python manage.py migrate` here*

### Honeypot Template Tag

Add the following template tag loader to your form page.

```html
{% load honeypot_tags %}
```

Add the Honeypot fields template tag anywhere inside the form

```html
<form>
...
{% honeypot_fields page.honeypot %}
...
</form>
```

In your Wagtail site you should now be able to add a new form page, *enable the honeypot field*.

Test that the honey pot field works

1. View the newly created form page.  
2. The honeypot field is visible and could be submitted with any value.  
3. Test it out by submitting the form with the honeypot field set to any value. It won't save the form submission or send an email if you have enabled that in your form page.

## Hide the Honeypot field

The honeypot field should be invisible to when viewed in a browser.

### Use CSS & JS to hide the honeypot field

The package has some basic css and javascript you can use to hide the field.

Example: add the following to your form template.

```html
<!-- recommended:
to add both but you can use one or the other -->

{% block extra_css %}
<link rel="stylesheet" href="{% static 'css/honeypot.css' %}">
{% endblock extra_css %}

<!-- alternative:
but without the css above loaded first
the field could be seen for a flash while the page loads -->

{% block extra_js %}
<script src="{% static 'js/honeypot.js' %}"></script>
{% endblock extra_js %}
```

The field should be visibly hidden and not be available to receive any value from a site visitor.

> When rendered, the fields will have the HTML attributes `tabindex="-1" autocomplete="off"` to prevent a site visitor from using the tab key to move to the field and disable any autocomplete browser functions.

## Developer Documentation

[Developer Docs](docs/developer.md) for detailed help.

## Versions

Wagtail honey pot can be used in environments:

- Python 3.9+
- Django 4.2+
- Wagtail 5.1+

## Contributions

Contributions or ideas to improve this package are welcome.
