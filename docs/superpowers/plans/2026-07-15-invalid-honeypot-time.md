# Invalid Honeypot Timestamp Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reject empty and non-numeric honeypot timestamps without raising an exception or processing the form submission.

**Architecture:** Keep timestamp validation inside `HoneypotFormSubmissionMixin.time_diff()`, which remains a boolean predicate. Conversion failures return `False`, allowing the existing `process_form_submission()` condition to ignore malformed submissions without changing template output or valid submission behavior.

**Tech Stack:** Python, Django, Wagtail, Django `TestCase`, Ruff, uv

## Global Constraints

- Preserve all existing `HONEYPOT_*` setting names and valid-input behavior.
- Preserve the existing `time_diff(value, interval)` interface and interval boundary semantics.
- Treat `TypeError` and `ValueError` from timestamp conversion as invalid honeypot input.
- Do not suppress invalid project configuration such as a non-numeric interval.
- Do not change templates, migrations, dependencies, or README usage documentation.
- Add a short user-facing entry under `CHANGELOG` → `Unreleased`.

---

### Task 1: Fail Closed for Malformed Honeypot Timestamps

**Files:**

- Modify: `tests/test_methods.py:19-31`
- Modify: `tests/test_form.py:93-103`
- Modify: `wagtail_honeypot/models.py:44-48`
- Modify: `CHANGELOG:5-8`

**Interfaces:**

- Consumes: `HoneypotFormSubmissionMixin.time_diff(value, interval)` and the existing `HoneypotFormPageTestCase.post_form(**overrides)` helper.
- Produces: unchanged `time_diff(value, interval) -> bool`; values that cannot be converted with `int(value)` produce `False`.

- [ ] **Step 1: Add focused method tests for invalid values**

Add this method after `test_time_diff_thresholds` in `tests/test_methods.py`:

```python
def test_time_diff_rejects_invalid_values(self):
    cases = [
        ("empty string", ""),
        ("non-numeric string", "not-a-timestamp"),
        ("none", None),
    ]

    for label, submitted_time in cases:
        with self.subTest(label=label):
            self.assertFalse(self.form.time_diff(submitted_time, self.interval))
```

- [ ] **Step 2: Add form-flow regression coverage**

Add this method after `test_form_submission_is_ignored_when_honeypot_time_is_too_short` in `TestHoneypotFormEnabled` in `tests/test_form.py`:

```python
def test_form_submission_is_ignored_when_honeypot_time_is_invalid(self):
    for value in ("", "not-a-timestamp"):
        with self.subTest(value=value):
            resp = self.post_form(whf_time=value)
            self.assert_submission_count(0)
            self.assertContains(resp, "Thank you for your message")
```

The response assertion protects the existing indistinguishable thank-you response, while the submission count proves the malformed request did not reach Wagtail's normal submission persistence path.

- [ ] **Step 3: Run the new tests and verify the regression**

Run:

```bash
uv run manage.py test \
  tests.test_methods.TestHoneypotMethods.test_time_diff_rejects_invalid_values \
  tests.test_form.TestHoneypotFormEnabled.test_form_submission_is_ignored_when_honeypot_time_is_invalid
```

Expected: `FAILED (errors=...)`; each malformed value reaches `wagtail_honeypot/models.py` and raises `TypeError` or `ValueError` from `int(value)`.

- [ ] **Step 4: Implement the minimal conversion guard**

Replace `time_diff()` in `wagtail_honeypot/models.py` with:

```python
@staticmethod
def time_diff(value, interval):
    now_time = str(time.time()).split(".")[0]
    try:
        submitted_time = int(value)
    except (TypeError, ValueError):
        return False
    diff = abs(int(now_time) - submitted_time)
    return True if diff > interval else False
```

Keep `int(now_time)` and the interval comparison outside the exception handler so project configuration and internal errors remain visible.

- [ ] **Step 5: Run the focused regression tests**

Run:

```bash
uv run manage.py test \
  tests.test_methods.TestHoneypotMethods.test_time_diff_rejects_invalid_values \
  tests.test_form.TestHoneypotFormEnabled.test_form_submission_is_ignored_when_honeypot_time_is_invalid
```

Expected: `Ran 2 tests` followed by `OK`.

- [ ] **Step 6: Add the changelog entry**

Add this flat entry beneath `## Unreleased` in `CHANGELOG`:

```markdown
- Ignore malformed honeypot timestamps instead of raising an exception.
```

- [ ] **Step 7: Run focused form and method coverage**

Run:

```bash
uv run manage.py test tests.test_methods tests.test_form
```

Expected: all method and form tests pass, including valid timestamp thresholds, accepted submissions, and every ignored-submission case.

- [ ] **Step 8: Run the complete test suite**

Run:

```bash
make test
```

Expected: the Django suite reports `OK`, and the coverage command exits successfully.

- [ ] **Step 9: Run lint and inspect the final diff**

Run:

```bash
make lint
git diff --check
git diff -- wagtail_honeypot/models.py tests/test_methods.py tests/test_form.py CHANGELOG
```

Expected: Ruff reports no errors, `git diff --check` prints nothing, and the diff contains only the conversion guard, regression tests, and changelog entry.

- [ ] **Step 10: Commit the fix**

```bash
git add wagtail_honeypot/models.py tests/test_methods.py tests/test_form.py CHANGELOG
git commit -m "fix: reject malformed honeypot timestamps"
```

Expected: one implementation commit containing the production fix, regression coverage, and changelog entry.
