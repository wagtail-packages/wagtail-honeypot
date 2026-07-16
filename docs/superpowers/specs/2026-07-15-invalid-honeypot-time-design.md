# Invalid Honeypot Timestamp Design

## Problem

When honeypot protection is enabled, `process_form_submission()` reads the configured timestamp field from untrusted POST data and passes it to `time_diff()`. The method converts the value with `int(value)` without validation. An empty or non-numeric value therefore raises `ValueError` and turns a rejected spam submission into a server error, as reported in GitHub issue #60.

This is a deterministic malformed-input case, not a timing or concurrency problem. Missing timestamp fields are already rejected without raising, so present-but-invalid timestamps should follow the same fail-closed behavior.

## Desired Behavior

- A timestamp that cannot be converted to an integer is invalid.
- Invalid timestamps cause the honeypot check to fail and the submission to be ignored.
- Rejected submissions continue to render the normal thank-you response without creating a `FormSubmission` or sending email.
- Valid timestamp handling and the configured `HONEYPOT_TIME_INTERVAL` boundary remain unchanged.
- Honeypot-disabled forms remain unchanged.

## Design

Keep timestamp conversion and validation inside `HoneypotFormSubmissionMixin.time_diff(value, interval)`. Wrap only the conversion of `value` in a `try` block and return `False` for `TypeError` or `ValueError`. A valid integer value continues through the existing elapsed-time comparison.

This preserves `time_diff()` as a boolean predicate and keeps all timestamp interpretation in one place. `process_form_submission()` requires no structural change: its existing `is_empty and is_delayed` condition will reject the submission when `time_diff()` returns `False`.

Do not broadly catch exceptions. In particular, an invalid project setting such as a non-numeric interval should remain visible as a configuration error rather than being silently classified as spam.

## Alternatives Considered

### Validate in `process_form_submission()`

The caller could validate the POST value before invoking `time_diff()`. This would prevent the exception but split timestamp rules across two methods and leave direct callers of `time_diff()` exposed to the same malformed input.

### Add a Django form field for the timestamp

Making the honeypot timestamp a declared form field would provide framework validation, but it would change how the package integrates with Wagtail forms and enlarge the public behavior surface for a small input-validation fix.

## Tests

Extend `tests/test_methods.py` with cases proving that `time_diff()` returns `False` for an empty string, a non-numeric string, and `None`. Retain the existing threshold cases to protect valid timestamp behavior.

Extend `tests/test_form.py` with enabled-honeypot submissions containing empty and non-numeric timestamp values. Each request must return the thank-you response and leave `FormSubmission.objects.count()` at zero. These tests verify the complete regression path from POST data through submission processing.

Run the focused method and form tests, the complete default test suite, and Ruff linting. No migration or README change is required.

## Documentation

Add a short entry under `CHANGELOG` → `Unreleased` stating that malformed honeypot timestamps are ignored instead of raising an exception.

## Compatibility

The change preserves all existing settings, template output, form-processing semantics for valid inputs, and supported Django/Wagtail versions. It narrows behavior only for timestamp values that currently crash request processing.
