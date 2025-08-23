## Goal
Replace deprecated `FetLife::base_url` references with `Connection::BASE_URL` and bump version to 1.28.5.

## Constraints
- Follow AGENTS.md instructions.
- Keep docs (AGENTS.md, toaster.md, README.markdown, plan.md) in sync.
- Run CI commands before committing.

## Risks
- Missed references could break generated links.
- CI commands may fail due to missing dependencies.

## Test Plan
- `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`
- `docker-compose build`
- `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"`

## Semver
Patch release: fix adapter links and bump version to 1.28.5.

## Repo Structure
- `adapter/public/index.php`: use `Connection::BASE_URL` for link generation.

## Affected Files
- adapter/public/index.php
- README.markdown
- toaster.md
- CHANGELOG.md
- pyproject.toml
- composer.json
- plan.md

## Rollback
Revert commit.

