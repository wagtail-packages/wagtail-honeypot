# Wagtail Honeypot

Use this package to add optional honeypot protection to your Wagtail forms.

![Alt text](docs/sample.jpg?raw=true "Title")

It should help to reduce form spam by tricking bots into submitting data in fields that should remain empty.

The package provides validation that a hidden text field that should remain empty and checks a time interval between the form being displayed and submitted.

## How it works

When the Wagtail Form is submitted and the honeypot protection is enabled, the honeypot fields & values are available in the `POST` data.

If the form is submitted with content in the hidden field or before the interval expires the submission is ignored.

- No email is sent
- No submission is stored
- The thank you page is always shown if available.

View the custom [HoneypotMixin](./wagtail_honeypot/models.py) for more information.

## Installation and setup

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

**A working minimal Wagtail example can inspected see [here](./tests/testapp/)**

### Use The Honeypot Model Mixins

The mixins add a honeypot enable/disable checkbox to your form page model and custom form submission method.

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
content_panels = content_panels + honeypot_panels
```

You'll need to run `makemigrations` and `migrate` here

### Add The Honeypot Template Tag to your form page template

To render the honeypot fields in your form page template use the provided template tag.

```html
{% load honeypot_tags %}
```

and add the Honeypot fields template tag anywhere inside the form

```html
<form>
...
{% honeypot_fields page.honeypot %}
...
</form>
```

**Create a form page and enable the Honeypot protection.**

## Hide the Honeypot field

View the newly created form page. You will see that the honeypot field is visible and could be submitted with any value. That would block the form submission and that's how it should work.

You can try it out by submitting the form with the honeypot field set to any value. It won't save the form submission or send it as an email if you have enabled that in your form page.

### Use CSS & JS to hide the honeypot field

Add the following CSS and JS to your form template

```html
{% block extra_js %}
<script src="{% static 'js/honeypot.js' %}"></script>
{% endblock extra_js %}

{% block extra_css %}
<link rel="stylesheet" href="{% static 'css/honeypot.css' %}">
{% endblock extra_css %}
```

The end result is the field should be visibly hidden and not be available to receive any value from a site visitor.

When rendered, the fields will have the HTML attributes `tabindex="-1" autocomplete="off"` to prevent a site visitor from using the tab key to move to the field and disable any autocomplete browser functions.

A more complete example is [form_page.html](wagtail_honeypot/templates/wagtail_honeypot_test/form_page.html) in the test app.

[View Developer Docs](docs/developer.md) for detailed help.

## Versions

Wagtail honey pot can be used in environments:

- Python 3.7+
- Django 3.2+
- Wagtail 4.1+

## Contributions

Contributions or ideas to improve this package are welcome.
