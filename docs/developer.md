# Configuration

Honeypot protection is a way to trick bots into submitting data in fields that should remain empty when submitted by a website visitor.  

The package provides a text field that should remain empty.  If the form is submitted with a value in this field the submission is ignored.  

## Honeypot Text Field

This is how the default honeypot text field is rerendered.

```html
<input type="text" name="whf_name" id="whf_name" data-whf_name="" tabindex="-1" autocomplete="off">
```

You can change the text field name by adding the following to your settings.

```python
HONEYPOT_NAME = "your-field-name"
```

It also provides a time field and checks a time interval between the form being displayed and submitted.

The default interval is 3 seconds. If the form is submitted before the interval expires the submission is ignored.

### Honeypot Time Field

This is how the default honeypot time field is rerendered.

```html
<input type="hidden" name="whf_time" id="whf_time" data-whf_name="" tabindex="-1" autocomplete="off">
```

You can change the time field name by adding the following to your settings.

```python
HONEYPOT_TIME = "your-field-name"
```

You can change the time interval by adding the following to your settings.

```python
HONEYPOT_INTERVAL = 1 # seconds
```

## Development Setup

There is a [testapp](../tests/testapp/) provided that is a fully configured minimal setup using Wagtail v4.2

Start the app:

```bash
make migrate
make superuser
make run
```

It's already initialised with admin login details of Username: `admin` Password: `changeme`

View the site at `http://localhost:8000` or add `/admin` to login.

You can see if emails are sent or not via the console.

### It's sometimes convenient to send emails via a SMTP server

If you have docker and docker-compose installed

- run `make mail` to spin up a Mailhog instance and simulate a `real` email inbox.
- view the Mailhog app in your browser at `http://localhost:8025`
- running this command will add a local.py file to settings in hte sandbox app with the correct EMAIL_BACKEND and credentials
