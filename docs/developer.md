# Developer setup and configuration

## Development Setup

Install [`uv`](https://docs.astral.sh/uv/) and use it as the default workflow for this project.

Pin or install the default contributor Python version:

```bash
uv python install 3.12
uv sync
```

The default synced environment is intended to track the latest tested local stack for this repo: Python 3.12 with Django 6.0 and Wagtail 7.3. Use `tox` for the broader compatibility matrix.

There is a [testapp](../tests/testapp/) provided that is a fully configured minimal setup using Wagtail v6.3+

Setup the app:

```bash
uv run python manage.py migrate
uv run python manage.py createsuperuser
make superuser
```

This adds an admin account with login details of Username: `admin` Password: `changeme`

Run the development server:

```bash
uv run python manage.py runserver 0:8000
```

View the site at `http://localhost:8000` or add `/admin` to login.

The `Makefile` targets also run through `uv`, so `make sync`, `make migrate`, `make run`, `make test`, and `make tox` remain valid shortcuts.

## Common commands

Run the default test suite:

```bash
uv run coverage run manage.py test
uv run coverage report
```

Run the compatibility matrix:

```bash
uv run tox --skip-missing-interpreters
```

Run the configured formatting and lint hooks:

```bash
uv run pre-commit run --all-files
```

Run Ruff directly:

```bash
uv run ruff check .
uv run ruff format .
```

Or use the Makefile shortcuts:

```bash
make lint
make format
```

See [Releasing wagtail-honeypot](contributing/releasing.md) for the maintainer release runbook.

## Dependency management

Use `uv` to change contributor dependencies and keep the lockfile in sync:

```bash
uv add --dev <package>
uv lock
uv sync
```

If you edit `pyproject.toml` manually, regenerate `uv.lock` and resync the environment before committing.

### A convenient SMTP server

If you have docker and docker-compose installed

```bash
make mail
```

> Will spin up a Mailhog instance and simulate a `real` email inbox.
View the Mailhog app in your browser at `http://localhost:8025`

Now when you submit the form with settings to send the notification email you will see the email in the Mailhog inbox

## Configuration

Optional configuration settings.

## Honeypot Text Field

You can change the text field name by adding the following to your settings.

```python
HONEYPOT_NAME_FIELD = "new-field-name"
```

The honeypot text field would be rendered ...

```html
<input type="text" name="new-field-name" id="new-field-name" data-new-field-name="" tabindex="-1" autocomplete="off" aria-hidden="true">
```

You can change the time field name and/or the time interval by adding the following to your settings.

```python
HONEYPOT_TIME_FIELD = "time-field-name"
HONEYPOT_TIME_INTERVAL = 1  # seconds
```

> The time field and checks a time interval between the form being displayed and submitted.  
The default interval is 3 seconds.  
If the form is submitted before the interval expires the submission is ignored.

### Honeypot Time Field

The honeypot time field would be rendered ...

```html
<input type="hidden" name="time-field-name" id="time-field-name" data-time-field-name="" tabindex="-1" autocomplete="off" aria-hidden="true">
```

### Custom process_form_submission method

This is a copy of the package process_form_submission() method.

If need be you can use this a basis and override it in your FormPage model and alter it for your own needs.

```python
class HoneypotFormSubmissionMixin(AbstractEmailForm):
    """
    Adds the overridden process_form_submission method to your form model
    """

    def process_form_submission(self, form):
        honeypot_name_field = getattr(settings, "HONEYPOT_NAME_FIELD", "whf_name")
        honeypot_time_field = getattr(settings, "HONEYPOT_TIME_FIELD", "whf_time")
        honeypot_time_interval = getattr(settings, "HONEYPOT_TIME_INTERVAL", 3)

        # honey pot disabled
        if not self.honeypot:
            return super().process_form_submission(form)

        # honeypot enabled
        score = []
        if honeypot_name_field in form.data and honeypot_time_field in form.data:
            score.append(form.data[honeypot_name_field] == "")
            score.append(self.time_diff(form.data[honeypot_time_field], honeypot_time_interval))
            return super().process_form_submission(form) if len(score) and all(score) else None

    @staticmethod
    def time_diff(value, interval):
        now_time = str(time.time()).split(".")[0]
        try:
            submitted_time = int(value)
        except (TypeError, ValueError):
            return False
        diff = abs(int(now_time) - submitted_time)
        return True if diff > interval else False

    class Meta:
        abstract = True
```
