# Wagtail 7.4 and Dependency Refresh Design

## Goal

Add explicit support and test coverage for Wagtail 7.4 LTS while refreshing every maintained dependency surface in the repository: the default development environment, the universal lockfile, pre-commit hooks, GitHub Actions, and CI database services.

## Compatibility Policy

- Preserve the published runtime requirements of Python 3.10 or newer and Wagtail 6.3 or newer.
- Preserve the existing Wagtail 6.3 and 7.0-7.3 tox coverage; this upgrade does not intentionally remove backward compatibility.
- Add Wagtail 7.4 only with combinations supported by Wagtail itself. Wagtail 7.4 supports Django 5.2 and 6.0 on Python 3.10-3.14, while Django 6.0 itself requires Python 3.12 or newer.
- Keep Django 4.2 coverage for older supported Wagtail releases, but never combine Django 4.2 with Wagtail 7.4.
- Do not change package version metadata, release tags, migrations, or public honeypot behavior.

Wagtail's official compatibility table and 7.4 upgrade notes are the authority for these constraints:

- <https://docs.wagtail.org/en/stable-7.4.x/releases/upgrading.html#compatible-django-python-versions>
- <https://docs.wagtail.org/en/stable-7.4.x/releases/7.4.html>

## Chosen Approach

Use one coordinated pull request with separately reviewable commits for compatibility coverage, dependency and workflow refreshes, and documentation. The Wagtail constraint, lockfile, tox factors, pre-commit hooks, and CI actions are coupled; updating them together avoids repeated lockfile and workflow churn while commit boundaries still make failures attributable.

Two alternatives were rejected:

1. A Wagtail-only upgrade would leave known stale Python tools, hooks, and actions in place and would not satisfy the requested full refresh.
2. Separate compatibility and tooling pull requests would isolate changes more strongly, but both would need to touch dependency resolution and CI, creating duplicate churn without a corresponding risk reduction for this small package.

## Repository Changes

### Default development environment

Update `pyproject.toml` so the dev group uses `Wagtail>=7.4,<7.5` with the existing `Django>=6.0,<6.1` constraint. Keep the package dependency `Wagtail>=6.3` and all Python and framework classifiers unchanged.

Refresh direct development tools to the current stable versions identified on 2026-07-15:

| Dependency | Current | Target |
| --- | ---: | ---: |
| Coverage | 7.13.5 | 7.15.2 |
| django-upgrade | 1.30.0 | 1.31.1 |
| pre-commit | 4.5.1 | 4.6.0 |
| Ruff | 0.15.11 | 0.15.21 |
| tox | 4.53.0 | 4.56.4 |

Only Ruff remains explicitly pinned in `pyproject.toml`, following the existing policy. The other direct tools remain unpinned and obtain their refreshed versions through `uv.lock`. `tox-gh-actions` is already current at 3.5.0 and stays unchanged.

Regenerate `uv.lock` with `uv lock --upgrade` after changing the Wagtail and Ruff constraints. This intentionally refreshes compatible transitive packages as well as direct tools. Review the diff to confirm that all changes are resolver-driven and that no prerelease is selected.

### Compatibility matrix

Add the tox dependency factor:

```ini
wagtail74: wagtail>=7.4,<7.5
```

Add SQLite coverage for these combinations:

| Python | Django | Wagtail |
| --- | --- | --- |
| 3.10, 3.11 | 5.2 | 7.4 |
| 3.12, 3.13, 3.14 | 5.2, 6.0 | 7.4 |

Keep all existing SQLite factors for Wagtail 6.3-7.3. Move the PostgreSQL and MySQL factors from `py314-django60-wagtail73` to `py314-django60-wagtail74` so the non-SQLite smoke tests exercise the newest compatibility line without increasing database-job count.

The package passed all tests in diagnostic runs on Python 3.10/Django 5.2/Wagtail 7.4 and Python 3.14/Django 6.0/Wagtail 7.4. No package implementation or test assertion changes are designed. Existing Treebeard manager warnings and the missing `tests/static` warning are not introduced by Wagtail 7.4 and remain outside this dependency upgrade.

### Pre-commit hooks

Update `.pre-commit-config.yaml` to these stable revisions:

| Hook | Target revision |
| --- | --- |
| `astral-sh/uv-pre-commit` | `0.11.29` |
| `astral-sh/ruff-pre-commit` | `v0.15.21` |
| `jackdewinter/pymarkdown` | `v0.9.39` |
| `adamchainz/django-upgrade` | `1.31.1` |

Synchronize the Ruff hook with the Ruff project pin. Change django-upgrade's target from Django 5.2 to Django 6.0 to match the default contributor stack, and remove the obsolete “replace with latest” comments.

### GitHub Actions and database services

Update workflow action references while retaining the repository's convention of major tags for GitHub-maintained actions and an exact release for `setup-uv`:

| Action | Current | Target |
| --- | --- | --- |
| `actions/checkout` | v3/v4 | v7 |
| `actions/setup-python` | v5 | v6 |
| `astral-sh/setup-uv` | v8.1.0 | v8.3.2 |
| `actions/upload-artifact` | v4 | v7 |
| `actions/download-artifact` | v4 | v8 |

Keep `pypa/gh-action-pypi-publish@release/v1`; it already tracks the current v1 release line. Keep the unversioned PostgreSQL service behavior unchanged. Change the MySQL service from `mysql:8.0` to `mysql:8.4`, the current MySQL LTS series, and validate the existing database settings and `mysqlclient` tox dependency against it. MySQL describes 8.4 as an LTS series: <https://dev.mysql.com/doc/refman/8.4/en/mysql-releases.html>.

Do not redesign the workflow structure or alter release behavior beyond action-version compatibility.

### Documentation and changelog

- Update `docs/developer.md` so the default local stack is Python 3.12, Django 6.0, and Wagtail 7.4.
- Update the test-app baseline wording from Wagtail 6.3+ only if needed for clarity; the public minimum remains Wagtail 6.3.
- Add a short, flat `CHANGELOG` entry under `## Unreleased` covering Wagtail 7.4 test support and the dependency/tooling refresh.
- Leave the README compatibility statement unchanged because the supported lower bounds do not change.

## Verification

Run verification in increasing scope:

1. `uv lock --check` to confirm the manifest and lockfile agree.
2. `uv run ruff check .` and `uv run ruff format . --check` for Python quality.
3. `uv run pre-commit run --all-files` to exercise every refreshed hook.
4. `uv run coverage run manage.py test` followed by `uv run coverage report` for the default Wagtail 7.4 stack.
5. Run every new Wagtail 7.4 SQLite factor explicitly, including both Django lines and all supported Python versions.
6. Run `py314-django60-wagtail74-postgres` and `py314-django60-wagtail74-mysql` where those services are available.
7. Run `uv run tox --skip-missing-interpreters` to exercise the complete locally available compatibility matrix.
8. Review GitHub Actions results for the full hosted matrix and both database services before declaring the pull request ready.

## Success Criteria

- Wagtail 7.4 is the default development version and has explicit tox coverage across every supported Python/Django combination.
- Existing Wagtail 6.3-7.3 compatibility coverage remains present.
- Direct Python tooling, transitive lockfile packages, pre-commit hooks, GitHub Actions, and the MySQL CI service are refreshed to the specified versions.
- The default tests, lint, format check, pre-commit suite, Wagtail 7.4 tox factors, and hosted CI all pass without package behavior changes.
- Developer documentation and the Unreleased changelog accurately describe the change.
