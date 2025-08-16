## Goal
Load stored subscriptions on bot startup so they persist across restarts and add a regression test.

## Constraints
- Follow AGENTS.md: run make fmt and make check before committing.
- Keep versioning and changelog consistent.

## Risks
- Scheduler jobs may execute during tests and call external services.

## Test Plan
- `make fmt`
- `make check`
- `pip-audit -r requirements.txt`
- `bash scripts/agents-verify.sh`

## Semver
Patch release: internal bug fix.

## Affected Packages
- Python bot
- PHP adapter (version bump only)

## Rollback
Revert the commit and reset versions.
