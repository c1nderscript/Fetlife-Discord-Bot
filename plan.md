## Goal
Enforce adapter authentication token requirement and document mandatory configuration.

## Constraints
- Follow AGENTS.md: run `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`, `docker-compose build`, and `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"` before committing.
- Run `pip-audit` and `docker run --rm -v $(pwd):/app composer audit`.
- Validate with `su nobody -s /bin/bash -c ./codex.sh fast-validate`.

## Risks
- Missing token may cause the adapter to reject all requests if misconfigured.
- Tests may fail to capture HTTP status codes in CLI execution.

## Test Plan
- `vendor/bin/phpunit tests/MissingTokenTest.php`
- `pip-audit`
- `docker run --rm -v $(pwd):/app composer audit`
- `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`
- `docker-compose build`
- `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"`
- `docker-compose -f tests/docker-compose.test.yml down || true`
- `su nobody -s /bin/bash -c ./codex.sh fast-validate`

## Semver
Patch release: backward-compatible security fix.

## Affected Files
- adapter/public/index.php
- tests/MissingTokenTest.php
- README.markdown
- docs/production.md
- CHANGELOG.md
- pyproject.toml
- composer.json
- plan.md
- toaster.md

## Rollback
Revert commit.
