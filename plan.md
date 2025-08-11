# Plan

## Goal
Ensure temporary cookie files are cleaned up and verify removal with PHPUnit.

## Constraints
- Follow repository conventions including changelog, version bump, and tests.
- Maintain existing login flow without external network dependencies in tests.

## Risks
- Improper cleanup could leave lingering files.
- Test may need to mock network interactions.

## Test Plan
- `make check`

## Semver
Patch: backward-compatible bug fix.
