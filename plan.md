# Plan

## Goal
Constrain `/fl subscribe` to valid types and document target formats while scheduling polls using stored subscription types.

## Constraints
- Use `discord.app_commands.choices` for `sub_type` limited to `events` or `writings`.
- Update command descriptions and docstrings for `target` (`user:<nickname>` for writings, `location:<...>` for events).
- When scheduling `poll_adapter`, pass the canonical `sub.type` from the database.
- Maintain existing behavior for filters and metrics.

## Risks
- Direct invocation in tests may bypass decorator validation.
- Fetching the stored subscription may fail if the database returns `None`.

## Test Plan
- `make check`

## Semver
Patch: bugfix and documentation.
