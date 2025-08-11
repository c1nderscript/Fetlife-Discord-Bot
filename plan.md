# Plan

## Goal
Add asynchronous client helpers to fetch user writings and group posts from the adapter service.

## Constraints
- Follow repository conventions including changelog, version bump, and tests.
- Mirror existing aiohttp usage without introducing new dependencies.

## Risks
- Incorrect endpoint URLs could break polling.
- Tests may need mocking to avoid network access.

## Test Plan
- `make check`

## Semver
Minor: backwards-compatible feature.
