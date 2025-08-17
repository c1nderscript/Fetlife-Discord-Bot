## Goal
Add reaction-role functionality that maps emoji reactions on specific messages to guild roles and applies or removes those roles automatically.

## Constraints
- Follow AGENTS.md: run `make fmt` and `make check` before committing.
- Commands must require the Manage Roles permission and validate inputs.
- Storage helpers should store mappings by message ID and emoji.

## Risks
- Misconfigured mappings may grant unintended permissions.
- Reaction events could exceed Discord rate limits.

## Test Plan
- `pytest bot/tests/test_reaction_roles.py`
- `make fmt`
- `make check`

## Semver
Minor release: adds a new feature for reaction-based role assignment.

## Affected Packages
- Python bot code
- Tests
- Documentation

## Rollback
Revert the commit and drop the `reaction_roles` table to restore previous behavior.
