## Goal
Add `asyncio` import to tasks and bump version to 1.28.9.

## Constraints
- Follow AGENTS.md instructions.
- Keep docs (AGENTS.md, toaster.md, README.markdown, plan.md) in sync.
- Run CI commands before committing.

## Risks
- Lint or type checks may fail if dependencies are missing.
- Adjusting imports could introduce unforeseen errors.

## Test Plan
- `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`
- `docker-compose build`
- `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"`

## Semver
Patch release: ensure tasks import `asyncio` and bump version to 1.28.9.

## Repo Structure
- `bot/tasks.py`: ensure asyncio import.

## Affected Files
- bot/tasks.py
- CHANGELOG.md
- README.markdown
- toaster.md
- pyproject.toml
- composer.json
- plan.md

## Rollback
Revert commit.
