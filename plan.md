## Goal
Add welcome system with configurable messages and optional verification via `/welcome setup`, send welcome messages on member join, assign roles after verification, preview messages, and log joins/leaves.

## Constraints
- Follow AGENTS.md: run `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`, `docker-compose build`, and `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"` before committing.
- Run `pip-audit` and `composer audit`.
- Validate with `su nobody -s /bin/bash -c ./codex.sh fast-validate`.

## Risks
- Misconfigured welcome messages could ping unintended roles.
- Verification bypass could grant roles without checks.
- Unhandled exceptions on join events could block onboarding.

## Test Plan
- `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`
- `docker-compose build`
- `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"`
- `pip-audit`
- `composer audit`
- `su nobody -s /bin/bash -c ./codex.sh fast-validate`

## Semver
Minor release: adds new welcome features without breaking existing APIs.

## Affected Packages
- `bot/welcome.py`
- `bot/main.py`
- `alembic/versions/0007_add_welcome_configs.py`
- `README.markdown`
- `toaster.md`
- `CHANGELOG.md`
- `pyproject.toml`
- `composer.json`

## Rollback
Revert commit.
