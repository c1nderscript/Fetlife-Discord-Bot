## Goal
Add moderation system with infractions table and moderation commands including `/warn`, `/mute`, `/kick`, `/ban`, `/timeout`, `/modlog`, `/purge`, plus appeal workflow scaffolding and dashboard stub.

## Constraints
- Follow AGENTS.md: run `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`, `docker-compose build`, and `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"` before committing.
- Run `pip-audit` and `composer audit`.
- Validate with `su nobody -s /bin/bash -c ./codex.sh fast-validate`.

## Risks
- Misconfigured permissions could allow abuse of moderation commands.
- Escalation logic might silence users more than intended.
- Purge filters risk deleting unintended messages.

## Test Plan
- `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`
- `docker-compose build`
- `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"`
- `pip-audit`
- `composer audit`
- `su nobody -s /bin/bash -c ./codex.sh fast-validate`

## Semver
Minor release: adds new features without breaking existing APIs.

## Affected Packages
- `bot/moderation.py`
- `bot/main.py`
- `README.markdown`
- `toaster.md`
- `CHANGELOG.md`
- `pyproject.toml`
- `composer.json`

## Rollback
Revert commit.
