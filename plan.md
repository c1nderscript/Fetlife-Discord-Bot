## Goal
Add regression test for HTTP adapter URL requirement and bump version to 1.28.4.

## Constraints
- Follow AGENTS.md instructions.
- Keep docs (AGENTS.md, toaster.md, README.markdown, plan.md) in sync.
- Run CI commands before committing.

## Risks
- CI commands may fail due to missing dependencies.
- New test may fail to trigger the expected SystemExit.

## Test Plan
- `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`
- `docker-compose build`
- `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"`

## Semver
Patch release: add test coverage for HTTPS adapter requirement and bump version to 1.28.4.

## Repo Structure
- `bot/tests/test_adapter_https.py`: ensures the bot exits when ADAPTER_BASE_URL uses HTTP without `MOCK_ADAPTER`.

## Affected Files
- bot/tests/test_adapter_https.py
- bot/tests/AGENTS.md
- bot/tests/test_web_interface.py
- bot/telegram_bridge.py
- README.markdown
- toaster.md
- CHANGELOG.md
- pyproject.toml
- composer.json
- plan.md

## Rollback
Revert commit.
