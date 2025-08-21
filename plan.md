## Goal
Ensure JsonFormatter serializes extra log fields like correlation_id.

## Constraints
- Follow AGENTS.md instructions.
- Run security audits and linters before committing.

## Risks
- Non-JSON-serializable extras could break logging.

## Test Plan
- `pip-audit`
- `composer audit`
- `black bot`
- `flake8 bot`
- `mypy bot`
- `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`
- `docker-compose -f tests/docker-compose.test.yml down || true`
- `su nobody -s /bin/bash -c ./codex.sh fast-validate`

## Semver
Patch release: backward-compatible logging fix.

## Affected Files
- bot/main.py
- bot/tests/test_main.py
- CHANGELOG.md
- pyproject.toml
- composer.json
- toaster.md
- plan.md

## Rollback
Revert commit.
