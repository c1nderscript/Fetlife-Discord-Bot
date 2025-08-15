## Goal
Prompt for adapter and Telegram credentials during setup and persist them to `.env`.

## Constraints
- Default to existing `.env` values when present.
- Use `write_env` for persistence.
- Update documentation, version files, and changelog.
- Follow existing code style and repository guidelines.

## Risks
- Misreading `.env` could capture incorrect values.
- Added prompts may confuse operators.

## Test Plan
- `make fmt`
- `make check`
- `bash scripts/agents-verify.sh`

## Semver
Patch release: setup improvements only.

## Affected Packages
- Python package `fetlife-discord-bot`
- PHP package `project/fetlife-discord-bot`

## Rollback
Revert the commit.
