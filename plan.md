## Goal
Add audit logging to record management actions and expose them via command and web UI.

## Constraints
- Follow AGENTS.md: run `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`, `docker-compose build`, and `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"` before committing.
- Update `pyproject.toml` and `composer.json` version numbers.
- Document the audit log feature in README.

## Risks
- Logging sensitive data could expose user information.
- Inefficient queries may slow the web UI.

## Test Plan
- `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`
- `docker-compose build`
- `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"`
- `pip-audit`
- `composer audit`
- `su nobody -s /bin/bash -c ./codex.sh\ fast-validate`

## Semver
Minor release: adds audit logging features.

## Affected Packages
- `bot/audit.py`
- `bot/models.py`
- `alembic/versions/*`
- `bot/main.py`
- `bot/tests/test_audit_log.py`
- `bot/tests/test_web_interface.py`
- `README.markdown`
- `pyproject.toml`
- `composer.json`
- `CHANGELOG.md`

## Rollback
Revert commits and drop `audit_log` table.
