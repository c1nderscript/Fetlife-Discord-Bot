## Goal
Add AGENTS.md for `adapter/public` and bump version to 1.28.3.

## Constraints
- Follow AGENTS.md instructions.
- Keep docs (AGENTS.md, toaster.md, README.markdown, plan.md) in sync.
- Run CI commands before committing.

## Risks
- CI commands may fail due to missing dependencies.
- New AGENTS file might miss required context.

## Test Plan
- `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`
- `docker-compose build`
- `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"`

## Semver
Patch release: documentation updates, bump version to 1.28.3.

## Repo Structure
- `adapter/public/AGENTS.md` documents the adapter HTTP entrypoint.

## Affected Files
- adapter/public/AGENTS.md
- README.markdown
- toaster.md
- CHANGELOG.md
- pyproject.toml
- composer.json
- plan.md

## Rollback
Revert commit.
