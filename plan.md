## Goal
Support quoted filter values in subscription commands and bump version to 1.26.6.

## Constraints
- Follow AGENTS.md instructions.
- Keep docs (AGENTS.md, toaster.md, README.markdown, plan.md) in sync.
- Run CI commands before committing.

## Risks
- Incorrect parsing could break existing subscriptions.
- CI commands may fail due to missing dependencies.

## Test Plan
- `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`
- `docker-compose build`
- `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"`

## Semver
Patch release: fix subscription command parsing and bump version to 1.26.6.

## Affected Files
- bot/utils.py
- bot/tests/test_utils.py
- CHANGELOG.md
- pyproject.toml
- composer.json
- README.markdown
- toaster.md
- plan.md

## Rollback
Revert commit.
