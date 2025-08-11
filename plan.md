# Plan

## Goal
Relay new events and writings from the adapter as Discord embeds during polling.

## Constraints
- Preserve existing dedupe, cursor, and metrics behavior.
- Support both `events` and `writings` subscription types using adapter client helpers.
- Follow repository conventions for changelog, version bump, and tests.

## Risks
- Unexpected payload fields could render incomplete embeds.
- Additional rate-limit calls may slow tests.

## Test Plan
- `make check`

## Semver
Minor: backwards-compatible feature.
