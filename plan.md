## Goal
Introduce a shared aiohttp ClientSession with a default timeout and ensure it is closed on shutdown.

## Constraints
- Follow AGENTS.md: run `make fmt` and `make check` before committing.
- Update tests, CHANGELOG.md, and documentation if needed.

## Risks
- Unclosed sessions could leak resources.
- Improper refactor may break adapter_client callers.

## Test Plan
- `make fmt`
- `make check`

## Semver
Patch release: internal refactor.

## Affected Packages
- Python bot code
- Tests

## Rollback
Revert the commit to restore per-call ClientSessions.
