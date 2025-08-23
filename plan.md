## Goal
Ensure `adapter_client` imports `logging` and bump version to 1.28.7.

## Constraints
- Follow AGENTS.md instructions.
- Keep docs (AGENTS.md, toaster.md, README.markdown, plan.md) in sync.
- Run CI commands before committing.

## Risks
- Lint or type checks may fail if dependencies are missing.
- Logging import changes could introduce unforeseen errors.

## Test Plan
- `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`
- `docker-compose build`
- `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"`

## Semver
Patch release: fix logging import and bump version to 1.28.7.

## Repo Structure
- `bot/adapter_client.py`: logging import.

## Affected Files
- bot/adapter_client.py
- CHANGELOG.md
- README.markdown
- toaster.md
- pyproject.toml
- composer.json
- plan.md

## Rollback
Revert commit.
