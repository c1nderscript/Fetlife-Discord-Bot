## Goal
Handle adapter 401 errors by re-authenticating affected accounts and retrying polls.

## Constraints
- Follow AGENTS.md: run make fmt and make check before committing.
- Include tests for 401 re-login logic.

## Risks
- Stored credentials may be invalid or unavailable, causing repeated failures.
- Additional login attempts could trigger rate limits.

## Test Plan
- `make fmt`
- `make check`
- `bash scripts/agents-verify.sh`

## Semver
Patch release: bug fix for adapter login recovery.

## Affected Packages
- Python bot
- Tests

## Rollback
Revert commit to remove 401 handling and tests.
