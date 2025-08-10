# Plan

## Goal
Handle invalid JSON in filter parsing within the `/fl subscribe` command and cover it with tests.

## Constraints
- Follow existing logging and rate limit patterns in `fl_subscribe`.
- Maintain repository conventions including changelog and version updates.

## Risks
- Misplaced error handling could still raise uncaught exceptions.
- Additional test may require event loop setup and mocking scheduler.

## Test Plan
- `make check`

## Semver
Patch: backwards compatible bug fix.
