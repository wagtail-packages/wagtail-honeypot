# Wagtail 7.4 and Dependency Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Release version 1.4.0 with Wagtail 7.0 through 7.4 support on compatible Django 5.2/6.0 combinations while refreshing the repository's Python dependencies, lockfile, pre-commit hooks, GitHub Actions, MySQL service, developer documentation, and changelog.

**Architecture:** Keep the package's public behavior unchanged while moving the default contributor stack to Wagtail 7.4 and retaining runtime support back to Wagtail 7.0. Use representative tox factors for Wagtail 7.0, 7.3, and 7.4 without creating unsupported Django/Python combinations.

**Tech Stack:** Python 3.10-3.14, Django 5.2/6.0, Wagtail 7.0/7.3/7.4, uv, tox, Ruff, pre-commit, GitHub Actions, PostgreSQL, MySQL 8.4.

## Global Constraints

- Preserve `requires-python = ">=3.10"` and set the runtime and development dependencies to `Wagtail>=7.0,<7.5`; retain Wagtail 7.4 in the lockfile as the default stack.
- Remove Django 4.2/5.1, Wagtail 6.3, and unused Wagtail 7.1/7.2 compatibility factors and classifiers.
- Test Wagtail 7.0 only with Django 5.2 and Python 3.10-3.13; test Wagtail 7.3/7.4 with Django 5.2 on Python 3.10-3.14 and Django 6.0 on Python 3.12-3.14.
- Set package version metadata to 1.4.0. Do not change release tags, migrations, public template output, or form-processing behavior.
- Use `uv` for project commands and Ruff for Python linting and formatting.
- Keep the existing untracked `.worktrees/` directory untouched.
- Add a flat user-facing entry under `CHANGELOG`'s `## Unreleased` section.

## File Map

- `pyproject.toml`: declares the default Wagtail development line and the Ruff version synchronized with pre-commit.
- `tox.ini`: declares the supported Django/Wagtail/Python compatibility factors and database smoke-test factors.
- `uv.lock`: records refreshed direct and transitive Python dependencies.
- `.pre-commit-config.yaml`: pins hook revisions and the default django-upgrade target.
- `.github/workflows/test.yml`: runs the compatibility matrix and database services.
- `.github/workflows/release.yml`: builds, transfers, and publishes release artifacts with current actions.
- `README.md`: documents the supported Wagtail, Django, and Python versions for package users.
- `docs/developer.md`: documents the default contributor stack.
- `CHANGELOG`: records the compatibility and maintenance changes for the next release.

---

### Task 1: Add Wagtail 7.4 to the default stack and retain Wagtail 7.0-7.4 support

**Files:**

- Modify: `pyproject.toml`
- Modify: `tox.ini`
- Modify: `uv.lock`

**Interfaces:**

- Consumes: the existing `django52`, `django60`, Python, database, and Wagtail tox factor conventions.
- Produces: representative `wagtail70`, `wagtail73`, and `wagtail74` dependency factors and 20 supported SQLite environments; later workflow tasks rely on `py314-django60-wagtail74-postgres` and `py314-django60-wagtail74-mysql`.

- [ ] **Step 1: Demonstrate that the Wagtail 7.4 tox environment is not yet defined**

Run:

```bash
uv run tox config -e py314-django60-wagtail74-sqlite | rg 'wagtail>=7\.4,<7\.5'
```

Expected: `rg` exits with status 1 because the environment has no Wagtail 7.4 dependency while `wagtail74` is absent from `tox.ini`.

- [ ] **Step 2: Update package metadata for the 1.4.0 support policy**

In `pyproject.toml`, set `version = "1.4.0"`, set the runtime and development constraints to `Wagtail>=7.0,<7.5`, and remove the Django 4.2, Django 5.1, and Wagtail 6 classifiers. Keep the supported Python classifiers and the Django 5.2, Django 6.0, and Wagtail 7 classifiers.

```toml
[dependency-groups]
dev = [
    "coverage",
    "Django>=6.0,<6.1",
    "django-upgrade",
    "pre-commit",
    "ruff==0.15.11",
    "tox",
    "tox-gh-actions",
    "Wagtail>=7.0,<7.5",
]
```

- [ ] **Step 3: Replace the tox environment list with current coverage**

Replace the `envlist` in `tox.ini` with:

```ini
envlist =
    py{310,311,312,313}-django52-wagtail{70,73,74}-sqlite
    py314-django52-wagtail{73,74}-sqlite
    py{312,313,314}-django60-wagtail{73,74}-sqlite
    py314-django60-wagtail74-{postgres,mysql}
```

This retains representative coverage from the Wagtail 7.0 support floor through the Wagtail 7.4 default stack without generating Wagtail 7.0 combinations that its official compatibility table excludes.

- [ ] **Step 4: Retain only current dependency factors**

Remove the `django42`, `django51`, `wagtail63`, `wagtail71`, and `wagtail72` dependency factors. Retain:

```ini
    django52: Django>=5.2,<5.3
    django60: Django>=6.0,<6.1
    wagtail70: wagtail>=7.0,<7.1
    wagtail73: wagtail>=7.3,<7.4
    wagtail74: wagtail>=7.4,<7.5
```

- [ ] **Step 5: Resolve the new default stack without performing the full tool upgrade yet**

Run:

```bash
uv lock
uv sync
uv tree --depth 1 --locked
```

Expected: the dev dependency is Wagtail 7.4.x, Django remains 6.0.x, and the lockfile is valid. Resolver-required transitive changes are acceptable; the intentional blanket upgrade happens in Task 2.

- [ ] **Step 6: Run every new SQLite compatibility factor**

Run:

```bash
uv run tox --skip-missing-interpreters --skip-env '.*-(postgres|mysql)$'
```

Expected: all 20 SQLite environments run 17 tests and report `OK`. The known Treebeard manager and missing `tests/static` warnings may still appear.

- [ ] **Step 7: Commit the compatibility matrix**

```bash
git add pyproject.toml tox.ini uv.lock
git commit -m "test: cover supported Wagtail 7 releases"
```

---

### Task 2: Refresh Python tooling, the lockfile, and pre-commit hooks

**Files:**

- Modify: `pyproject.toml`
- Modify: `.pre-commit-config.yaml`
- Modify: `uv.lock`

**Interfaces:**

- Consumes: the broad Wagtail 7.0-7.4 constraint and Wagtail 7.4 locked default from Task 1.
- Produces: a lockfile with current stable dependencies and synchronized Ruff/django-upgrade local and hook configuration.

- [ ] **Step 1: Record the stale direct dependency report**

Run:

```bash
uv tree --outdated --depth 1 --locked
```

Expected before the refresh: the report identifies older locked versions of Coverage, django-upgrade, pre-commit, Ruff, and tox. Wagtail should already be on 7.4.x from Task 1.

- [ ] **Step 2: Update the Ruff project pin**

In `pyproject.toml`, change only this dev dependency:

```toml
    "ruff==0.15.21",
```

- [ ] **Step 3: Replace the pre-commit configuration with synchronized stable revisions**

Update `.pre-commit-config.yaml` to:

```yaml
repos:
  - repo: https://github.com/astral-sh/uv-pre-commit
    rev: 0.11.29
    hooks:
      - id: uv-lock
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.15.21
    hooks:
      - id: ruff-check
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/jackdewinter/pymarkdown
    rev: v0.9.39
    hooks:
      - id: pymarkdown
        args:
          - --disable-rules
          - line-length
          - scan
  - repo: https://github.com/adamchainz/django-upgrade
    rev: "1.31.1"
    hooks:
      - id: django-upgrade
        args: [--target-version, "6.0"]
```

- [ ] **Step 4: Upgrade all compatible locked packages**

Run:

```bash
uv lock --upgrade
uv sync
uv lock --check
```

Expected: resolution succeeds with Wagtail 7.4.x and no prerelease packages.

- [ ] **Step 5: Verify the intended direct tool versions**

Run:

```bash
uv tree --depth 1 --locked
```

Expected direct versions:

```text
wagtail v7.4.2
coverage v7.15.2
django-upgrade v1.31.1
pre-commit v4.6.0
ruff v0.15.21
tox v4.56.4
tox-gh-actions v3.5.0
```

Django may resolve to the newest 6.0.x patch release. Review `git diff -- uv.lock` and confirm all remaining changes are transitive resolver updates.

- [ ] **Step 6: Exercise every refreshed hook**

Run:

```bash
uv run pre-commit run --all-files
git diff --check
```

Expected: every hook passes and no hook rewrites tracked files.

- [ ] **Step 7: Commit the tooling refresh**

```bash
git add pyproject.toml .pre-commit-config.yaml uv.lock
git commit -m "chore: refresh Python development tooling"
```

---

### Task 3: Refresh GitHub Actions and the MySQL service

**Files:**

- Modify: `.github/workflows/test.yml`
- Modify: `.github/workflows/release.yml`

**Interfaces:**

- Consumes: the Wagtail 7.4 database tox factors from Task 1.
- Produces: hosted CI using current action runtimes and MySQL 8.4 LTS; release publishing behavior remains otherwise unchanged.

- [ ] **Step 1: Capture the stale workflow references**

Run:

```bash
rg -n 'actions/checkout|actions/setup-python|astral-sh/setup-uv|actions/(upload|download)-artifact|mysql:' .github/workflows
```

Expected before editing: test jobs use `actions/checkout@v3`, release uses `actions/checkout@v4` and `actions/setup-python@v5`, setup-uv uses v8.1.0, artifact actions use v4, and MySQL uses 8.0.

- [ ] **Step 2: Update test workflow actions and MySQL**

Apply these replacements throughout `.github/workflows/test.yml`:

```yaml
uses: actions/checkout@v7
```

```yaml
uses: astral-sh/setup-uv@v8.3.2
```

```yaml
image: mysql:8.4
```

There must be three checkout updates, three setup-uv updates, and one MySQL image update. Do not change the PostgreSQL service or job structure.

- [ ] **Step 3: Update release workflow actions**

Apply these replacements in `.github/workflows/release.yml`:

```yaml
uses: actions/checkout@v7
```

```yaml
uses: actions/setup-python@v6
```

```yaml
uses: astral-sh/setup-uv@v8.3.2
```

```yaml
uses: actions/upload-artifact@v7
```

```yaml
uses: actions/download-artifact@v8
```

Keep `pypa/gh-action-pypi-publish@release/v1` unchanged.

- [ ] **Step 4: Parse both workflow files as YAML**

Run:

```bash
uv run python -c 'from pathlib import Path; import yaml; [yaml.safe_load(path.read_text()) for path in Path(".github/workflows").glob("*.yml")]; print("workflow YAML parsed")'
```

Expected: `workflow YAML parsed` with exit status 0.

- [ ] **Step 5: Verify every workflow reference and database tox dependency resolves**

Run:

```bash
rg -n 'actions/checkout|actions/setup-python|astral-sh/setup-uv|actions/(upload|download)-artifact|pypa/gh-action-pypi-publish|image:' .github/workflows
uv run tox -e py314-django60-wagtail74-postgres,py314-django60-wagtail74-mysql --notest
```

Expected: only the target action versions appear, PostgreSQL remains unversioned, MySQL is 8.4, and tox successfully provisions both database environments without running tests.

- [ ] **Step 6: Commit the workflow refresh**

```bash
git add .github/workflows/test.yml .github/workflows/release.yml
git commit -m "ci: refresh actions and database coverage"
```

---

### Task 4: Update contributor documentation and changelog

**Files:**

- Modify: `README.md`
- Modify: `docs/developer.md`
- Modify: `CHANGELOG`

**Interfaces:**

- Consumes: the final default stack and maintenance scope from Tasks 1-3.
- Produces: contributor-facing documentation and the required Unreleased summary.

- [ ] **Step 1: Update the documented default stack**

In `docs/developer.md`, replace the existing default-stack sentence with:

```markdown
The default synced environment is intended to track the latest tested local stack for this repo: Python 3.12 with Django 6.0 and Wagtail 7.4. Use `tox` for the broader compatibility matrix.
```

Keep the test-app statement on the default Wagtail 7.4 stack. Update the README compatibility section to Wagtail 7.0 through 7.4 and Django 5.2/6.0, and link to Wagtail's compatibility table so users select a supported pairing.

- [ ] **Step 2: Add the Unreleased changelog entries**

Under `## Unreleased` in `CHANGELOG`, retain the existing branch-workflow entry and add:

```markdown
- Release version 1.4.0 with Wagtail 7.0 through 7.4 support on compatible Django 5.2 and 6.0 combinations.
- Drop support for Django 4.2 and 5.1, and Wagtail versions before 7.0; earlier package releases remain available for older projects.
- Refresh locked development dependencies, pre-commit hooks, GitHub Actions, and MySQL CI to current releases.
```

- [ ] **Step 3: Verify documentation formatting and stated versions**

Run:

```bash
uvx --from pymarkdownlnt pymarkdown --disable-rules line-length scan README.md docs/developer.md docs/contributing/releasing.md docs/superpowers/specs/2026-07-15-wagtail-7-4-dependency-refresh-design.md docs/superpowers/plans/2026-07-15-wagtail-7-4-dependency-refresh.md
rg -n 'Wagtail 7\.[034]|Wagtail 6\.3\+|## Unreleased|pre-commit hooks' README.md docs/developer.md CHANGELOG
git diff --check
```

Expected: Markdown scanning and whitespace checks pass; user docs show Wagtail 7.0 through 7.4 support while developer docs retain Wagtail 7.4 as the default stack; the version, support-policy, and tooling changelog entries appear under Unreleased.

- [ ] **Step 4: Run final local verification**

Run:

```bash
uv lock --check
uv run ruff check .
uv run ruff format . --check
uv run pre-commit run --all-files
uv run coverage run manage.py test
uv run coverage report
uv run tox --skip-missing-interpreters --skip-env '.*-(postgres|mysql)$'
git diff --check
```

Expected: lock, lint, formatting, hooks, the 17-test default suite, coverage report, and every locally available SQLite tox environment pass. GitHub Actions must run the PostgreSQL and MySQL test environments before PR readiness.

- [ ] **Step 5: Commit documentation and changelog**

```bash
git add README.md docs/developer.md CHANGELOG
git commit -m "docs: document supported Wagtail 7 releases"
```

---

### Task 5: Review branch readiness and prepare the pull request handoff

**Files:**

- Review: all files changed from `main`

**Interfaces:**

- Consumes: all completed implementation commits and verification output.
- Produces: an evidence-backed handoff with an accurate PR title and body; pushing or opening the PR requires the user's authorization.

- [ ] **Step 1: Review the complete branch diff and commit sequence**

Run:

```bash
git status --short --branch
git log --oneline --decorate main..HEAD
git diff --stat main...HEAD
git diff --check main...HEAD
```

Expected: only the design, plan, compatibility, dependency/tooling, workflow, documentation, changelog, and resolver-driven lockfile changes are present; `.worktrees/` remains untracked and unmodified.

- [ ] **Step 2: Prepare exact pull request metadata**

Use this title:

```text
Prepare 1.4.0 for Wagtail 7.0 through 7.4
```

Use this body, replacing none of its scope statements:

```markdown
## Summary

- retain Wagtail 7.0 through 7.4 support with representative compatibility coverage
- refresh Python dependencies, pre-commit hooks, GitHub Actions, and MySQL CI
- release 1.4.0 with Wagtail 7.0 through 7.4 support on compatible Django 5.2 and 6.0 combinations

## Verification

- `uv lock --check`
- `uv run ruff check .`
- `uv run ruff format . --check`
- `uv run pre-commit run --all-files`
- `uv run coverage run manage.py test`
- `uv run coverage report`
- `uv run tox --skip-missing-interpreters --skip-env '.*-(postgres|mysql)$'`
- GitHub Actions SQLite, PostgreSQL, and MySQL jobs
```

- [ ] **Step 3: Confirm hosted verification after an authorized push**

After the user authorizes publishing and the branch is pushed, require the SQLite matrix plus PostgreSQL and MySQL jobs to pass. Do not describe the upgrade as PR-ready until those hosted checks succeed.
