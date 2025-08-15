## Goal
Ensure release-hygiene workflow fails when the `composer.json` version diverges from `pyproject.toml` or is not SemVer.

## Constraints
- Follow existing code style and repository guidelines.
- Bump Python and PHP versions together.
- Insert the check after the current Python version guard.

## Risks
- Extra CI step slightly increases runtime.
- Misformatted version fields could cause false failures.

## Test Plan
- `make fmt`
- `make check`
- `bash scripts/agents-verify.sh`

## Semver
Patch release: CI enforcement only.

## Affected Packages
- Python package `fetlife-discord-bot`
- PHP package `project/fetlife-discord-bot`

## Rollback
Revert the commit.
