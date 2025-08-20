## Goal
Add config drift detection script with optional remediation and document usage; bump minor version.

## Constraints
- Follow AGENTS.md: run `docker-compose build`, `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"`, and `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test` before committing.
- Run `pip-audit` and `docker run --rm -v $(pwd):/app composer audit`.
- Validate with `su nobody -s /bin/bash -c ./codex.sh fast-validate`.

## Risks
- Overwriting deployed configuration during remediation if path mis-specified.
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
Minor release: adds new drift detection script.

## Affected Files
- scripts/drift-check.sh
- README.markdown
- CHANGELOG.md
- pyproject.toml
- composer.json
- toaster.md
- plan.md

## Rollback
Revert commit.
