## Goal
Add CODEOWNERS file assigning maintainers to key directories to enforce review policy.

## Constraints
- Follow AGENTS.md: run `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`, `docker-compose build`, and `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"` before committing.

## Risks
- Incorrect owner handles could block merges or fail to require review.
- CODEOWNERS patterns may not match actual directories.

## Test Plan
- docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test
- docker-compose build
- docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"
- pip-audit
- composer audit

## Semver
Patch release: repository metadata only.

## Affected Packages
- Repository configuration

## Rollback
Revert the commit and remove CODEOWNERS entries from the repository, AGENTS, and CHANGELOG.
