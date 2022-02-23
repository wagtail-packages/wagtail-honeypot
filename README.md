# Wagtail Honeypot

Use this package to add a optional honeypot field to your wagtail forms.

## How it works

When the Wagtail Form is submitted, and the honeypot field is enabled the honeypot field & value is in the `POST` data.

If the field value contains any text the form is not processed...

```python
# process_form_submission is overriding the function in AbstractEmailForm

def process_form_submission(self, form):
    honeypot_name = getattr(settings, "HONEYPOT_NAME", "whf_name")
    if honeypot_name in form.data and not form.data[honeypot_name]:
        # the submission is returned only if the honeypot field is empty
        return super().process_form_submission(form)

```

The function above will block the notification emails that are sent and the saving of the form data. You can provide your own `process_form_submission` method if you need an alternative behaviour.

## Installation

```bash
pip install wagtail-honeypot
```

## Wagtail Setup

The default honey pot field name is `whf_name`. The name is used when the field is rendered...

```html
<input type="text" name="whf_name" id="whf_name" data-whf_name="" tabindex="-1" autocomplete="off">
```

If you would like to changed the field name, you can do so by adding the following to your settings.

```bash
HONEYPOT_NAME="foo"
```

The field would then be rendered...

```html
<input type="text" name="foo" id="foo" data-foo="" tabindex="-1" autocomplete="off">
```

*The name of the field is used to identify the honey pot field when the form is submitted.*

### Honeypot Template Tag

To render the honeypot field in your form page template use the provided template tag.

```python
{% load honeypot_tags %}  # load the template tag

<form>
...
{% honeypot_field %}  # add the honeypot field to your form
...
</form>
```

### Honeypot Model Mixin

The mixin will add a honeypot field to your form page model.

`honeypot = models.BooleanField(default=False, verbose_name="Honeypot Enabled")`

 It also adds a form panel you can use.

If you follow the official Wagtail docs for the [Form Builder](https://docs.wagtail.org/en/stable/reference/contrib/forms/index.html) your form should look something like this...

```python
class FormPage(HoneypotMixin):  # use HoneypotMixin in pace of AbstractEmailForm
    intro = RichTextField(blank=True)
    thank_you_text = RichTextField(blank=True)

    content_panels = HoneypotMixin.content_panels + [
        FieldPanel('intro', classname="full"),
        InlinePanel('form_fields', label="Form fields"),
        FieldPanel('thank_you_text', classname="full"),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('from_address', classname="col6"),
                FieldPanel('to_address', classname="col6"),
            ]),
            FieldPanel('subject'),
        ], "Email"),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(HoneypotMixin.honeypot_panels, heading='Honeypot'),
        ObjectList(Page.promote_panels, heading='Promote'),  # a tab for the honeypot settings
        ObjectList(Page.settings_panels, heading='Settings', classname="settings"),
    ])
```

### Hide the Honeypot field

If you create a form now you will see that the honeypot field is visible and could be submitted with any value. That would block the form submission and that's how it should work.

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

The end result is the field should be visibly hidden and not be available to receive any value form a site visitor. When rendered, the input field will have the html attributes `tabindex="-1" autocomplete="off"` to prevent a site visitor from using the tab key to move to the field and disable any autocomplete browser feature.

A more complete example is [form_page.html](wagtail_honeypot/templates/wagtail_honeypot_test/form_page.html) from the package test files.

## Todo

- add a time check for form submission
