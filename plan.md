## Goal
Introduce a reusable health-check script to verify bot and adapter endpoints and wire Makefile target to use it.

## Constraints
- Follow AGENTS.md: run `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`, `docker-compose build`, and `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"` before committing.
- Run `pip-audit` and `composer audit`.
- Validate with `su nobody -s /bin/bash -c ./codex.sh fast-validate`.

## Risks
- Script may fail when containers aren't running.
- Root detection might block legitimate usage.

## Test Plan
- `./scripts/health-check.sh`
- `docker-compose build`
- `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"`
- `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`
- `docker-compose -f tests/docker-compose.test.yml down || true`
- `docker run --rm -v $(PWD):/app composer audit`
- `pip-audit`
- `su nobody -s /bin/bash -c ./codex.sh fast-validate`

## Semver
Patch release: CI helper script.

## Affected Files
- `scripts/health-check.sh`
- `Makefile`
- `README.markdown`
- `CHANGELOG.md`
- `pyproject.toml`
- `composer.json`
- `toaster.md`
- `plan.md`

## Rollback
Revert commit.
