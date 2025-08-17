## Goal
Add an aiohttp-based management web interface for administrating subscriptions, role mappings, and channel settings, secured via Discord OAuth2 login.

## Constraints
- Serve the interface at configurable `MGMT_PORT`.
- Restrict access to user IDs listed in `ADMIN_IDS` after Discord OAuth2 login.
- Store session data in HMAC-signed cookies using `SESSION_SECRET`.
- Follow AGENTS.md: run `make fmt` and `make check` before committing.

## Risks
- Incorrect OAuth configuration could expose admin pages.
- Invalid input may corrupt stored channel settings.

## Test Plan
- `pytest bot/tests/test_web_interface.py`
- `make fmt`
- `make check`

## Semver
Minor release: adds a new management UI secured by Discord OAuth2.

## Affected Packages
- Python bot code
- Tests
- Documentation

## Rollback
Revert the commit and remove the new environment variables to restore previous behavior.
