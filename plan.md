## Goal
Add management page to list, add, and remove FetLife accounts and bump version to 1.27.0.

## Constraints
- Follow AGENTS.md instructions.
- Keep docs (AGENTS.md, toaster.md, README.markdown, plan.md) in sync.
- Run CI commands before committing.

## Risks
- Credentials may be stored incorrectly or duplicate accounts might be added.
- CI commands may fail due to missing dependencies.

## Test Plan
- `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`
- `docker-compose build`
- `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"`

## Semver
Minor release: add accounts management UI and bump version to 1.27.0.

## Affected Files
- bot/main.py
- bot/templates/accounts.html
- bot/templates/AGENTS.md
- README.markdown
- toaster.md
- CHANGELOG.md
- pyproject.toml
- composer.json
- plan.md

## Rollback
Revert commit.
