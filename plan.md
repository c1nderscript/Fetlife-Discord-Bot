## Goal
Add moderation management web forms for warn, mute, kick, ban, timeout, and purge actions.

## Constraints
- Follow AGENTS.md: run `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`, `docker-compose build`, and `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"` before committing.
- Run `pip-audit` and `composer audit`.
- Validate with `su nobody -s /bin/bash -c ./codex.sh fast-validate`.

## Risks
- Input validation for moderation forms may be insufficient.
- Moderation actions may fail if Discord objects cannot be resolved.

## Test Plan
- `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`
- `docker-compose build`
- `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"`
- `pip-audit`
- `composer audit`
- `su nobody -s /bin/bash -c ./codex.sh fast-validate`

## Semver
Minor release: adds moderation web forms.

## Affected Files
- `bot/main.py`
- `bot/moderation.py`
- `bot/tests/test_moderation_forms.py`
- `README.markdown`
- `CHANGELOG.md`
- `pyproject.toml`
- `composer.json`
- `plan.md`

## Rollback
Revert commit.
