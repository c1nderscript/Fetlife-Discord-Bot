## Goal
Include extra fields like `correlation_id` in JSON log output.

## Constraints
- Follow AGENTS.md: run `black bot`, `flake8 bot`, `mypy bot`, and `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test` before committing.
- Run `pip-audit` and `docker run --rm -v $(pwd):/app composer audit`.
- Validate with `su nobody -s /bin/bash -c ./codex.sh fast-validate`.

## Risks
- Failing to exclude standard LogRecord fields could cause noisy or incorrect log output.
- Dependency or Docker tooling may be unavailable, causing validation to fail.

## Test Plan
- `black bot`
- `flake8 bot`
- `mypy bot`
- `pip-audit`
- `docker run --rm -v $(pwd):/app composer audit`
- `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`
- `docker-compose -f tests/docker-compose.test.yml down || true`
- `su nobody -s /bin/bash -c ./codex.sh fast-validate`

## Semver
Patch release: backward-compatible fix.

## Affected Files
- bot/main.py
- bot/tests/test_main.py
- CHANGELOG.md
- pyproject.toml
- composer.json
- plan.md

## Rollback
Revert commit.
