## Goal
Default `scripts/setup.sh` to a dry run requiring `--confirm` for changes and document the new safety flags across docs.

## Constraints
- Follow AGENTS.md instructions.
- Keep docs (AGENTS.md, toaster.md, README.markdown, plan.md) in sync.
- Run CI commands before committing.

## Risks
- Interactive script changes could break prompts.
- CI commands may fail due to missing dependencies.

## Test Plan
- `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`
- `docker-compose build`
- `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"`

## Semver
Patch release: update setup script behavior and docs, bump version to 1.28.4.

## Repo Structure
- `scripts/AGENTS.md` documents setup script.

## Affected Files
- scripts/setup.sh
- scripts/AGENTS.md
- README.markdown
- toaster.md
- CHANGELOG.md
- pyproject.toml
- composer.json
- plan.md

## Rollback
Revert commit.

