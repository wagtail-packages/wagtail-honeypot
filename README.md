# Wagtail Honeypot

Use this package to add optional honeypot proection to your Wagtail forms.

Honey pot protection is a way to trick bots into submitting data in fields that should remain empty. The package prvides a text field that should remain empty and checks a time interval between the form being displayed and submitted. The defualt interval is 3 seconds. If the form is submitted before the interval expires the submission is ignored.

## How it works

When the Wagtail Form is submitted, and the honeypot protection is enabled the honeypot fields & values are in the `POST` data.

- If the fields and values are valid or the Honeypot feature is not enabled then the form is submitted normally.
- If the Honeypot feature is enabled and the validation fails the form is not processed but visibly and to a bot the form was successfully submitted.

```python
# process_form_submission is overriding the function in AbstractEmailForm

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

```

You can provide your own `process_form_submission` method if you need an alternative behaviour.

## Installation

```bash
pip install wagtail-honeypot
```

## Wagtail Setup

### Settings

Add the package to your settings

```python
INSTALLED_APPS = [
    ...
    "wagtail_honeypot",
    ...
]
```

### Honeypot Text Field

```html
<input type="text" name="whf_name" id="whf_name" data-whf_name="" tabindex="-1" autocomplete="off">
```

*You can change the text field name by adding the following to your settings.*

```python
HONEYPOT_NAME="foo"
```

### Honeypot Time Field

```html
<input type="hidden" name="whf_time" id="whf_time" data-whf_name="" tabindex="-1" autocomplete="off">
```

*You can change the time field name by adding the following to your settings.*

```python
HONEYPOT_TIME="bar"
```

*You can change the time interval by adding the following to your settings.*

```python
HONEYPOT_INTERVAL=1
```

### Honeypot Template Tag

To render the honeypot fields in your form page template use the provided template tag.

```python
{% load honeypot_tags %}  # load the template tag

<form>
...
{% honeypot_fields %}  # add the honeypot fields to your form
...
</form>
```

### Honeypot Model Mixin

The mixin will add a honeypot field to your form page model.

`honeypot = models.BooleanField(default=False, verbose_name="Honeypot Enabled")`

 It also adds a form panel you can use.

If you follow the official Wagtail docs for the [Form Builder](https://docs.wagtail.org/en/stable/reference/contrib/forms/index.html) your form should look something like this...

```python
class FormPage(HoneypotMixin):  # <-- add the mixin
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

    # add a edit_handler to enable the Honeypot tab
    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(HoneypotMixin.honeypot_panels, heading="Honeypot"),
            ObjectList(Page.promote_panels, heading="Promote"),
            ObjectList(Page.settings_panels, heading="Settings", classname="settings"),
        ]
    )
```

**Create a form page and enable the Honeypot protection.**

### Hide the Honeypot field

View the newly created form page. You will see that the honeypot field is visible and could be submitted with any value. That would block the form submission and that's how it should work.

You can try it out by submitting the form with the honeypot field set to any value. It won't save the form submission.

#### Use css to hide the honeypot field

Add the following css style to your own sites css...

```css
input[data-whf_name] {
    position: absolute;
    top: 0;
    left: 0;
    margin-left: 100vw;
}
```

#### Use javascript to hide the honeypot field

```javascript
var whf_name = "whf_name";
var data_whf_name = "[data-" + whf_name + "]";

document.querySelectorAll(data_whf_name).forEach(function(el) {
    el.classList.add(whf_name);
    el.setAttribute("style", "position: absolute;top: 0;left: 0;margin-left: 100%;");
});
```

The end result is the field should be visibly hidden and not be available to receive any value form a site visitor.

 When rendered, the fields will have the html attributes `tabindex="-1" autocomplete="off"` to prevent a site visitor from using the tab key to move to the field and disable any autocomplete browser functions.

A more complete example is [form_page.html](wagtail_honeypot/templates/wagtail_honeypot_test/form_page.html) from the package test files.
