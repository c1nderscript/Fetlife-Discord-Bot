## Goal
Release version 1.20.0 adding configurable retryable health checks and updating CI and documentation.

## Constraints
- Follow AGENTS.md: run `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`, `docker-compose build`, and `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"` before committing.
- Run `pip-audit` and `composer audit`.
- Validate with `su nobody -s /bin/bash -c ./codex.sh fast-validate`.

## Risks
- Docker or language tooling may be unavailable, causing tests or audits to fail.

## Test Plan
- `docker-compose build`
- `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"`
- `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`
- `docker-compose -f tests/docker-compose.test.yml down || true`
- `pip-audit`
- `docker run --rm -v $(PWD):/app composer audit`
- `su nobody -s /bin/bash -c ./codex.sh fast-validate`

## Semver
Minor release: adds configurable health-check retries without breaking APIs.

## Affected Files
- scripts/health-check.sh
- Makefile
- .github/workflows/deploy-validation.yml
- README.markdown
- CHANGELOG.md
- pyproject.toml
- composer.json
- plan.md

## Rollback
Revert commit.
