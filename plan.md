## Goal
Add dry-run default and --confirm flag to scripts/install.sh, document usage, and bump version to 1.28.0.

## Constraints
- Follow AGENTS.md instructions.
- Keep docs (AGENTS.md, toaster.md, README.markdown, plan.md) in sync.
- Run CI commands before committing.

## Risks
- Missing --confirm could lead to accidental operations if logic is wrong.
- CI commands may fail due to missing dependencies.

## Test Plan
- `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`
- `docker-compose build`
- `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"`

## Semver
Minor release: require --confirm for install actions and add --dry-run default, bump version to 1.28.0.

## Affected Files
- scripts/install.sh
- scripts/AGENTS.md
- README.markdown
- toaster.md
- CHANGELOG.md
- pyproject.toml
- plan.md

## Rollback
Revert commit.
