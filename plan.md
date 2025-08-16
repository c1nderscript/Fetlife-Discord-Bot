## Goal
Pause polling after consecutive adapter failures, notify channels, and expose subscription status via `/fl health`.

## Constraints
- Follow AGENTS.md: run `make fmt` and `make check` before committing.
- Update tests under `bot/tests/test_poll_adapter.py`.
- Bump versions and CHANGELOG consistently.

## Risks
- Paused subscriptions may miss updates.
- Failure counts reset on bot restart.

## Test Plan
- `make fmt`
- `make check`

## Semver
Minor release: adds new feature.

## Affected Packages
- Python bot
- PHP adapter metadata

## Rollback
Revert commit to restore previous polling behavior.
