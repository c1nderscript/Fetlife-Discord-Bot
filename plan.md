## Goal
Rate-limit administrative slash commands using Discord.py cooldowns with per-guild configuration.

## Constraints
- Follow AGENTS.md: run `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`, `docker-compose build`, and `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"` before committing.
- Update `pyproject.toml` and `composer.json` version numbers.
- Document new settings in README and example `config.yaml`.

## Risks
- Overly strict defaults could block legitimate admin actions.
- Misconfigured guild overrides may bypass intended limits.

## Test Plan
- `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`
- `docker-compose build`
- `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"`
- `pip-audit`
- `composer audit`
- `su nobody -s /bin/bash -c ./codex.sh\ fast-validate`

## Semver
Minor release: adds configurable command rate limiting.

## Affected Packages
- `bot/main.py`
- `bot/config.py`
- `bot/tests/test_config.py`
- `bot/tests/test_admin_cooldown.py`
- `config.yaml`
- `README.markdown`
- `pyproject.toml`
- `composer.json`
- `CHANGELOG.md`

## Rollback
Revert commits to remove cooldown checks and restore prior configuration and documentation.
