## Goal
Cache events, profiles, and RSVP records before relaying to Discord.

## Constraints
- Follow AGENTS.md: run `make fmt` and `make check` before committing.
- Update tests under `bot/tests` for new cache behavior.
- Keep documentation and changelog in sync.

## Risks
- Parsing event timestamps may fail.
- Cache tables may grow without pruning.

## Test Plan
- `make fmt`
- `make check`

## Semver
Patch release: internal reliability improvement.

## Affected Packages
- Python bot

## Rollback
Revert commit to restore previous polling behavior.
