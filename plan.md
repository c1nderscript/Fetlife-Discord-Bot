## Goal
Enforce that `ADAPTER_BASE_URL` values start with `https://` and exit with a clear
error message when they do not. Update environment loading and repository
documentation accordingly.

## Constraints
- Follow AGENTS.md: run `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`, `docker-compose build`, and `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"` before committing.
- Update `pyproject.toml` and `composer.json` version numbers.
- Mention HTTPS requirement in README and `AGENTS.md`.

## Risks
- Failing to update all references could confuse operators.
- Changing default may break environments not configured for TLS.

## Test Plan
- docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test
- docker-compose build
- docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"
- pip-audit
- composer audit
- ./codex.sh fast-validate

## Semver
Patch release: defaults and documentation.

## Affected Packages
- `bot/main.py`
- `README.markdown`
- `AGENTS.md`
- `pyproject.toml`
- `composer.json`

## Rollback
Revert commit to restore HTTP default and prior documentation.
