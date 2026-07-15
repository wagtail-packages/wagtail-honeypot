# Wagtail 7.4 and Dependency Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add and verify Wagtail 7.4 LTS support while refreshing the repository's Python dependencies, lockfile, pre-commit hooks, GitHub Actions, MySQL service, developer documentation, and changelog.

**Architecture:** Keep the package's public behavior and lower compatibility bounds unchanged. Extend the existing tox factor model with only Wagtail-supported 7.4 combinations, make 7.4 the default development line, and refresh each tooling surface in a separate reviewable commit before running full verification.

**Tech Stack:** Python 3.10-3.14, Django 4.2/5.1/5.2/6.0, Wagtail 6.3/7.0-7.4, uv, tox, Ruff, pre-commit, GitHub Actions, PostgreSQL, MySQL 8.4.

## Global Constraints

- Preserve `requires-python = ">=3.10"` and the runtime dependency `Wagtail>=6.3`.
- Preserve every existing Wagtail 6.3-7.3 SQLite compatibility factor.
- Test Wagtail 7.4 only with Django 5.2 or 6.0; test Django 6.0 only on Python 3.12 or newer.
- Do not change package version metadata, release tags, migrations, public template output, or form-processing behavior.
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
- `docs/developer.md`: documents the default contributor stack.
- `CHANGELOG`: records the compatibility and maintenance changes for the next release.

---

### Task 1: Add Wagtail 7.4 to the default stack and tox matrix

**Files:**

- Modify: `pyproject.toml`
- Modify: `tox.ini`
- Modify: `uv.lock`

**Interfaces:**

- Consumes: the existing `django52`, `django60`, Python, database, and Wagtail tox factor conventions.
- Produces: a `wagtail74` dependency factor and eight supported Wagtail 7.4 SQLite environments; later workflow tasks rely on `py314-django60-wagtail74-postgres` and `py314-django60-wagtail74-mysql`.

- [ ] **Step 1: Demonstrate that the Wagtail 7.4 tox environment is not yet defined**

Run:

```bash
uv run tox config -e py314-django60-wagtail74-sqlite | rg 'wagtail>=7\.4,<7\.5'
```

Expected: `rg` exits with status 1 because the environment has no Wagtail 7.4 dependency while `wagtail74` is absent from `tox.ini`.

- [ ] **Step 2: Change the default development Wagtail line**

In `pyproject.toml`, replace the Wagtail dev constraint and leave every other entry unchanged for this task:

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
    "Wagtail>=7.4,<7.5",
]
```

- [ ] **Step 3: Extend the tox environment list without removing older coverage**

Replace the `envlist` in `tox.ini` with:

```ini
envlist =
    py{310,311,312}-django42-wagtail{63,70,71,72,73}-sqlite
    py{312,313}-django{51,52}-wagtail{70,71,72}-sqlite
    py{312,313}-django{52,60}-wagtail73-sqlite
    py314-django60-wagtail73-sqlite
    py{310,311}-django52-wagtail74-sqlite
    py{312,313,314}-django{52,60}-wagtail74-sqlite
    py314-django60-wagtail74-{postgres,mysql}
```

This retains the existing Python 3.14/Django 6.0/Wagtail 7.3 SQLite factor while moving only the database smoke-test factors to Wagtail 7.4.

- [ ] **Step 4: Define the Wagtail 7.4 dependency factor**

Add this line immediately after the `wagtail73` dependency in `tox.ini`:

```ini
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
uv run tox -e py310-django52-wagtail74-sqlite,py311-django52-wagtail74-sqlite,py312-django52-wagtail74-sqlite,py312-django60-wagtail74-sqlite,py313-django52-wagtail74-sqlite,py313-django60-wagtail74-sqlite,py314-django52-wagtail74-sqlite,py314-django60-wagtail74-sqlite
```

Expected: all eight environments run 15 tests and report `OK`. The known Treebeard manager and missing `tests/static` warnings may still appear.

- [ ] **Step 7: Commit the compatibility matrix**

```bash
git add pyproject.toml tox.ini uv.lock
git commit -m "test: add Wagtail 7.4 compatibility coverage"
```

---

### Task 2: Refresh Python tooling, the lockfile, and pre-commit hooks

**Files:**

- Modify: `pyproject.toml`
- Modify: `.pre-commit-config.yaml`
- Modify: `uv.lock`

**Interfaces:**

- Consumes: the Wagtail 7.4 default constraint from Task 1.
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

Keep the following Wagtail 6.3+ test-app statement unchanged because it documents the package's retained lower bound.

- [ ] **Step 2: Add the Unreleased changelog entries**

Under `## Unreleased` in `CHANGELOG`, retain the existing branch-workflow entry and add:

```markdown
- Add Wagtail 7.4 testing coverage across its supported Django and Python versions.
- Refresh locked development dependencies, pre-commit hooks, GitHub Actions, and MySQL CI to current releases.
```

- [ ] **Step 3: Verify documentation formatting and stated versions**

Run:

```bash
uvx --from pymarkdownlnt pymarkdown --disable-rules line-length scan README.md docs/developer.md docs/contributing/releasing.md docs/superpowers/specs/2026-07-15-wagtail-7-4-dependency-refresh-design.md docs/superpowers/plans/2026-07-15-wagtail-7-4-dependency-refresh.md
rg -n 'Wagtail 7\.4|Wagtail 6\.3\+|## Unreleased|pre-commit hooks' docs/developer.md CHANGELOG
git diff --check
```

Expected: Markdown scanning and whitespace checks pass; developer docs show Wagtail 7.4 as the default and Wagtail 6.3+ as the retained test-app baseline; both new changelog entries appear under Unreleased.

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

Expected: lock, lint, formatting, hooks, the 15-test default suite, coverage report, and every locally available SQLite tox environment pass. GitHub Actions must run the PostgreSQL and MySQL test environments before PR readiness.

- [ ] **Step 5: Commit documentation and changelog**

```bash
git add docs/developer.md CHANGELOG
git commit -m "docs: document Wagtail 7.4 development support"
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
Add Wagtail 7.4 support and refresh dependencies
```

Use this body, replacing none of its scope statements:

```markdown
## Summary

- add Wagtail 7.4 coverage across supported Django and Python combinations
- refresh Python dependencies, pre-commit hooks, GitHub Actions, and MySQL CI
- document Wagtail 7.4 as the default contributor stack while retaining Wagtail 6.3+

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
