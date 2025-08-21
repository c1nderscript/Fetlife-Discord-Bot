## Goal
Document major directories with AGENTS.md files and bump version to 1.26.5.

## Constraints
- Follow AGENTS.md instructions.
- Keep docs (AGENTS.md, toaster.md, README.markdown, plan.md) in sync.
- Run CI commands before committing.

## Risks
- Documentation may become inconsistent.
- CI commands may fail due to missing dependencies.

## Test Plan
- `pip-audit`
- `composer audit`
- `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`
- `docker-compose build`
- `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"`

## Semver
Patch release: add AGENTS documentation and version bump.

## Affected Files
- AGENTS.md files
- pyproject.toml
- composer.json
- CHANGELOG.md
- toaster.md
- plan.md
- README.markdown

## Rollback
Revert commit.
