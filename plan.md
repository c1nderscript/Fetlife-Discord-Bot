## Goal
Allow the Discord bot to run when Telegram credentials are absent.

## Constraints
- Follow existing code style and repository guidelines.
- Bump Python and PHP versions together.

## Risks
- Conditional bridge creation may introduce attribute errors if not handled everywhere.
- Tests might require environment isolation to simulate missing credentials.

## Test Plan
- `make fmt`
- `make check`

## Semver
Patch release: fix optional Telegram bridge handling.

## Affected Packages
- Python package `fetlife-discord-bot`
- PHP package `project/fetlife-discord-bot`

## Rollback
Revert the commit.
