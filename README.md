# Wagtail Honeypot

Use this package to add optional honeypot protection to your Wagtail forms.

![Alt text](docs/sample.jpg?raw=true "Title")

It should help to reduce form spam by tricking bots into submitting data in fields that should remain empty.

The package provides validation that a hidden text field that should remain empty and checks a time interval between the form being displayed and submitted.

## How it works

When the Wagtail Form is submitted and the honeypot protection is enabled, the honeypot fields & values are available in the `POST` data.

If the form is submitted with content in the hidden field or before the interval expires the submission is ignored.

- No email is be sent
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

### Use The Honeypot Model Mixin

The mixin adds a honeypot enable/disable checkbox to your form page model.

`honeypot = models.BooleanField(default=False, verbose_name="Honeypot Enabled")`

It also adds a form panel you can use.

If you follow the official Wagtail docs for the [Form Builder](https://docs.wagtail.org/en/stable/reference/contrib/forms/index.html) your form should look something like this...

```python
from wagtail_honeypot.models import HoneypotMixin

class FormPage(HoneypotMixin):

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

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            # Honeypot Tab
            ObjectList(HoneypotMixin.honeypot_panels, heading="Honeypot"),
            ObjectList(HoneypotMixin.promote_panels, heading="Promote"),
            ObjectList(
                HoneypotMixin.settings_panels, heading="Settings", classname="settings"
            ),
        ]
    )

    # OR add a the honeypot checkbox without the extra tab
    content_panels = content_panels + HoneypotMixin.honeypot_panels
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

### Use CSS to hide the honeypot field

Add the following CSS style to your own site's CSS...

```css
input[data-whf_name] {
    position: absolute;
    top: 0;
    left: 0;
    margin-left: 100vw;
}
```

### and/or Use Javascript to hide the honeypot field

```javascript
var whf_name = "whf_name";
var data_whf_name = "[data-" + whf_name + "]";

document.querySelectorAll(data_whf_name).forEach(function(el) {
    el.classList.add(whf_name);
    el.setAttribute("style", "position: absolute;top: 0;left: 0;margin-left: 100%;");
});
```

The end result is the field should be visibly hidden and not be available to receive any value from a site visitor.

When rendered, the fields will have the HTML attributes `tabindex="-1" autocomplete="off"` to prevent a site visitor from using the tab key to move to the field and disable any autocomplete browser functions.

A more complete example is [form_page.html](wagtail_honeypot/templates/wagtail_honeypot_test/form_page.html) from the package test files.

## Versions

Wagtail honey pot can be used in environments:

- Python 3.7+
- Django 3.2+
- Wagtail 4.1+

## Contributions

Contributions or ideas to improve this package are welcome. [See Developer Docs](docs/developer.md)
