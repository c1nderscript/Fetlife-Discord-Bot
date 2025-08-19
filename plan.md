## Goal
Add deployment validation script to ensure required env vars are set, database connectivity works, and a TLS certificate exists.

## Constraints
- Follow AGENTS.md: run `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`, `docker-compose build`, and `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"` before committing.
- Run `pip-audit` and `composer audit`.
- Validate with `su nobody -s /bin/bash -c ./codex.sh fast-validate`.

## Risks
- Missing Postgres client or TLS certificate may cause false negatives.

## Test Plan
- `su nobody -s /bin/bash -c ./scripts/deploy-validate.sh`
- `docker-compose build`
- `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"`
- `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`
- `docker-compose -f tests/docker-compose.test.yml down || true`
- `docker run --rm -v $(PWD):/app composer audit`
- `pip-audit`
- `su nobody -s /bin/bash -c ./codex.sh fast-validate`

## Semver
Patch release: add deployment validation script.

## Affected Files
- scripts/deploy-validate.sh
- README.markdown
- toaster.md
- CHANGELOG.md
- pyproject.toml
- composer.json
- plan.md

## Rollback
Revert commit.
