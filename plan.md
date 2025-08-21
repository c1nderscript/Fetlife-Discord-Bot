## Goal
Ensure adapter_request propagates task cancellation by re-raising asyncio.CancelledError.

## Constraints
- Follow AGENTS.md: run `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`, `docker-compose build`, and `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"` before committing.
- Run `pip-audit` and `composer audit`.
- Validate with `su nobody -s /bin/bash -c ./codex.sh fast-validate`.

## Risks
- Missing cancellation may stall shutdown sequences.
- Integration tests may fail to run in this environment.

## Test Plan
- `pip-audit`
- `composer audit`
- `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`
- `docker-compose build`
- `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"`
- `docker-compose -f tests/docker-compose.test.yml down || true`
- `su nobody -s /bin/bash -c ./codex.sh fast-validate`

## Semver
Patch release: backward-compatible bug fix.

## Affected Files
- bot/main.py
- bot/tests/test_adapter_request.py
- pyproject.toml
- composer.json
- CHANGELOG.md
- plan.md

## Rollback
Revert commit.
