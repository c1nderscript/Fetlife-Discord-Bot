## Goal
Add deployment validation workflow and gate pull requests on make health.

## Constraints
- Follow AGENTS.md: run `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`, `docker-compose build`, and `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"` before committing.
- Run `pip-audit` and `composer audit`.
- Validate with `su nobody -s /bin/bash -c ./codex.sh fast-validate`.

## Risks
- Health scripts may fail due to missing services or env vars.

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
Patch release: CI workflow improvements.

## Affected Files
- .github/workflows/deploy-validation.yml
- .github/workflows/release-hygiene.yml
- CHANGELOG.md
- pyproject.toml
- composer.json
- toaster.md
- plan.md

## Rollback
Revert commit.
