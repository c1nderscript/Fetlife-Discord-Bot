## Goal
Default adapter connection uses HTTPS and documentation notes requirement with environment variable override.

## Constraints
- Follow AGENTS.md: run `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`, `docker-compose build`, and `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"` before committing.
- Update `pyproject.toml` and `composer.json` version numbers.
- Mention HTTPS requirement in README and `.env.example`.

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
- `.env.example`
- `pyproject.toml`
- `composer.json`

## Rollback
Revert commit to restore HTTP default and prior documentation.
