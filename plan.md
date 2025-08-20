## Goal
Ensure deployment validation and release hygiene workflows run `make health --confirm` with retry logic, execute backup and disaster-recovery validation scripts, upload monitoring dashboard artifacts, and bump minor version with CHANGELOG entry.

## Constraints
- Follow AGENTS.md: run `docker-compose build`, `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"`, and `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test` before committing.
- Run `pip-audit` and `docker run --rm -v $(pwd):/app composer audit`.
- Validate with `su nobody -s /bin/bash -c ./codex.sh fast-validate`.

## Risks
- Workflow retries or DR simulations may hang or fail unexpectedly.
- Docker or dependency tooling may be unavailable, causing tests or audits to fail.

## Test Plan
- `docker-compose build`
- `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"`
- `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`
- `docker-compose -f tests/docker-compose.test.yml down || true`
- `pip-audit`
- `docker run --rm -v $(pwd):/app composer audit`
- `su nobody -s /bin/bash -c ./codex.sh fast-validate`

## Semver
Minor release: adds workflow validation features.

## Affected Files
- .github/workflows/deploy-validation.yml
- .github/workflows/release-hygiene.yml
- CHANGELOG.md
- pyproject.toml
- composer.json
- plan.md
- toaster.md

## Rollback
Revert commit.
