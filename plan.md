## Goal
Document test fixtures with an AGENTS file and bump version to 1.28.6.

## Constraints
- Follow AGENTS.md instructions.
- Keep docs (AGENTS.md, toaster.md, README.markdown, plan.md) in sync.
- Run CI commands before committing.

## Risks
- Fixture descriptions could drift from JSON content.
- CI commands may fail due to missing dependencies.

## Test Plan
- `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`
- `docker-compose build`
- `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"`

## Semver
Patch release: add documentation and bump version to 1.28.6.

## Repo Structure
- `bot/tests/fixtures/AGENTS.md`: document JSON fixtures.

## Affected Files
- bot/tests/fixtures/AGENTS.md
- CHANGELOG.md
- README.markdown
- toaster.md
- pyproject.toml
- composer.json
- plan.md

## Rollback
Revert commit.
