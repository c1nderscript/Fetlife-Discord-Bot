# Plan

## Goal
Ensure select test files run standalone by adding missing imports and path adjustments.

## Constraints
- Preserve existing test logic.
- Use `# noqa: E402` for imports after path manipulations.

## Risks
- Path modifications may conceal other import issues.

## Test Plan
- Run `flake8` on modified tests.
- Execute each test module with `python` to confirm no import errors.
- Attempt `make check` (fails without Docker).
- Run `pytest` on modified tests to surface runtime issues.

## Semver
Patch bump to v0.1.1.
