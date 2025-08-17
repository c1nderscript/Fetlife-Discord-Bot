## Goal
Improve `codex.sh` safety: permit non-destructive commands when run as root, warn on unsafe usage, and replace `eval` with direct command invocation.

## Constraints
- Follow AGENTS.md: run `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`, `docker-compose build`, and `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"` before committing.
- Maintain `codex.sh` executable bit and default `--dry-run` behavior.

## Risks
- Misclassifying commands could allow destructive operations as root.
- Removing `eval` might break commands relying on shell features.

## Test Plan
- docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test
- docker-compose build
- docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"
- pip-audit
- composer audit

## Semver
Patch release: security hardening of tooling.

## Affected Packages
- Repository scripts (`codex.sh`)

## Rollback
Revert the commit to restore previous root check and `eval` usage.
