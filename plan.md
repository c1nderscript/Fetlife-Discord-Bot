## Goal
Add birthday reminders with /birthday commands, daily announcements, optional role assignment, time zones, and web UI calendar.

## Constraints
- Follow AGENTS.md: run `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`, `docker-compose build`, and `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"` before committing.
- Run `pip-audit` and `composer audit`.
- Validate with `su nobody -s /bin/bash -c ./codex.sh fast-validate`.

## Risks
- Incorrect time zone handling could miss or duplicate announcements.
- Privacy settings might expose dates if misconfigured.

## Test Plan
- `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`
- `docker-compose build`
- `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"`
- `pip-audit`
- `composer audit`
- `su nobody -s /bin/bash -c ./codex.sh fast-validate`

## Semver
Minor release: adds new feature without breaking existing APIs.

## Affected Packages
- `bot/birthday.py`
- `bot/main.py`
- `bot/models.py`
- `bot/tests/test_birthday_commands.py`
- `README.markdown`
- `CHANGELOG.md`
- `toaster.md`
- `pyproject.toml`
- `composer.json`

## Rollback
Revert commit.
