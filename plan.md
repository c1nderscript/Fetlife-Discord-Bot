## Goal
Remove the global `# mypy: ignore-errors` from `bot/storage.py` and add precise
type annotations so the file passes `mypy`.

## Constraints
- Follow AGENTS.md: run `make fmt` and `make check` before committing.
- Update calling code and tests impacted by stricter types.

## Risks
- Extensive use of `cast` may obscure future type issues.
- Missed call sites could break if return types change.

## Test Plan
- `mypy bot/storage.py`
- `make fmt`
- `make check`

## Semver
Patch release: internal type-hint improvements.

## Affected Packages
- Python bot code
- Tests

## Rollback
Revert the commit to restore previous typing behaviour.
