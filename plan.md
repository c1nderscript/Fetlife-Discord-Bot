# Plan

## Goal
Add Docker-based integration test harness simulating `/fl subscribe` flow with mock adapter and wire into `make check`.

## Constraints
- Use docker compose to launch bot test container and mock adapter.
- Integration test must operate without Discord or real FetLife access.
- Keep changes minimal and avoid modifying runtime logic.

## Risks
- Docker may be unavailable in some environments, causing tests to fail.
- Mock adapter responses could drift from real adapter behavior.

## Test Plan
- `docker compose -f tests/docker-compose.test.yml run --rm bot-test` to execute integration test.
- `make check` (build, lint, unit tests, integration test, phpunit).

## Semver
Patch bump to v0.1.4.
