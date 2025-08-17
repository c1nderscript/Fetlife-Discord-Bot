## Goal
Align project version across metadata files and changelog for the 1.4.0 release.

## Constraints
- Follow AGENTS.md instructions and repository policies.

## Risks
- Docker or dependency issues could block CI commands.
- Version mismatch might break packaging.

## Test Plan
- docker-compose build
- docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"
- docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test
- pip-audit
- composer audit
- ./codex.sh

## Semver
Minor release: new features warrant bump from 1.3.x to 1.4.0.

## Affected Packages
- pyproject.toml
- composer.json
- CHANGELOG.md

## Rollback
Revert the commit and restore previous version numbers in affected files.
