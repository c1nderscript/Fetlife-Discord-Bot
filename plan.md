## Goal
Provide `.env.example` template and reference it in docs and setup script.

## Constraints
- Follow existing code style and repository guidelines.
- Bump Python and PHP versions together.

## Risks
- Sample values may mislead users if defaults change.
- Setup script copy might overwrite existing config unintentionally.

## Test Plan
- `make fmt`
- `make check`

## Semver
Patch release: documentation and setup improvements.

## Affected Packages
- Python package `fetlife-discord-bot`
- PHP package `project/fetlife-discord-bot`

## Rollback
Revert the commit.
