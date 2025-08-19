## Goal
Document health check and deploy validation scripts and their integration with `make health` and CI.

## Constraints
- Follow AGENTS.md: run `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`, `docker-compose build`, and `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"` before committing.
- Run `pip-audit` and `composer audit`.
- Validate with `su nobody -s /bin/bash -c ./codex.sh fast-validate`.

## Risks
- Scripts may fail if required environment variables or database are missing.

## Test Plan
- `./scripts/health-check.sh`
- `./scripts/deploy-validate.sh`
- `make health`
- `docker-compose build`
- `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"`
- `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`
- `docker-compose -f tests/docker-compose.test.yml down || true`
- `docker run --rm -v $(PWD):/app composer audit`
- `pip-audit`
- `su nobody -s /bin/bash -c ./codex.sh fast-validate`

## Semver
Patch release: documentation update.

## Affected Files
- README.markdown
- CHANGELOG.md
- plan.md

## Rollback
Revert commit.
