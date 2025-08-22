## Goal
Reorganize documentation by moving `libFetLife` sections into `docs/libfetlife.md`, rewrite the README opening to describe the bot/adapter architecture, and bump version to 1.28.1.

## Constraints
- Follow AGENTS.md instructions.
- Keep docs (AGENTS.md, toaster.md, README.markdown, plan.md) in sync.
- Run CI commands before committing.

## Risks
- Cross-file version mismatch could confuse releases.
- CI commands may fail due to missing dependencies.

## Test Plan
- `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`
- `docker-compose build`
- `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"`

## Semver
Patch release: documentation updates and refactor, bump version to 1.28.1.

## Affected Files
- README.markdown
- docs/libfetlife.md
- docs/AGENTS.md
- toaster.md
- CHANGELOG.md
- pyproject.toml
- composer.json
- plan.md

## Rollback
Revert commit.
