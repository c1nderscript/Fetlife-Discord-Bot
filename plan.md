## Goal
Add timed message auto-deletion with `/timer` and `/autodelete` commands, persistence, and metrics.

## Constraints
- Follow AGENTS.md: run `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`, `docker-compose build`, and `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"` before committing.
- Run `pip-audit` and `composer audit`.
- Validate with `su nobody -s /bin/bash -c ./codex.sh fast-validate`.

## Risks
- Discord API errors could leave messages undeleted.
- Misconfigured timers might remove messages unexpectedly.

## Test Plan
- `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`
- `docker-compose build`
- `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"`
- `pip-audit`
- `composer audit`
- `su nobody -s /bin/bash -c ./codex.sh fast-validate`

## Semver
Minor release: new features.

## Affected Packages
- `bot/main.py`
- `bot/models.py`
- `bot/tasks.py`
- `alembic/versions/0006_add_timed_messages.py`
- `CHANGELOG.md`
- `README.markdown`
- `toaster.md`
- `pyproject.toml`
- `composer.json`
- `bot/tests/test_timer_commands.py`

## Rollback
Revert commit.
