## Goal
Add backup verification and disaster recovery validation scripts, wire them into CI as optional manual jobs, bump patch version, update docs.

## Constraints
- Follow AGENTS.md: run `docker-compose build`, `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"`, and `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test` before committing.
- Run `pip-audit` and `composer audit`.
- Validate with `su nobody -s /bin/bash -c ./codex.sh fast-validate`.

## Risks
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
Patch release: adds CI scripts and documentation.

## Affected Files
- scripts/backup-verify.sh
- scripts/dr-validate.sh
- .github/workflows/backup-dr.yml
- README.markdown
- CHANGELOG.md
- pyproject.toml
- composer.json
- plan.md

## Rollback
Revert commit.
