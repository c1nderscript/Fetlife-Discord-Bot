## Goal
Expose polling, timed message, moderation appeal, and welcome configuration controls via the management web UI and document the new capabilities.

## Constraints
- Follow AGENTS.md: run `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`, `docker-compose build`, and `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"` before committing.
- Run `pip-audit` and `composer audit`.
- Validate with `su nobody -s /bin/bash -c ./codex.sh fast-validate`.

## Risks
- Web handlers may expose unsecured inputs if validation is insufficient.
- Discord interactions may fail during timed message scheduling.

## Test Plan
- `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`
- `docker-compose build`
- `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"`
- `pip-audit`
- `composer audit`
- `su nobody -s /bin/bash -c ./codex.sh fast-validate`

## Semver
Minor release: adds new management web features.

## Affected Files
- `bot/main.py`
- `bot/tests/test_web_interface.py`
- `README.markdown`
- `CHANGELOG.md`
- `pyproject.toml`
- `composer.json`
- `plan.md`

## Rollback
Revert commit.
