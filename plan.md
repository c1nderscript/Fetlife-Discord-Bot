# Plan

## Goal
Add a unit test covering writings subscriptions to ensure `poll_adapter` sends Discord messages and updates the cursor.

## Constraints
- Mock `adapter_client.fetch_writings` to avoid network calls.
- Reuse existing `bot/tests/fixtures/writing.json` for sample payload.
- Patch Discord and scheduler interactions to keep the test self-contained.

## Risks
- Incorrect patching could leave background jobs running or unawaited coroutines.
- Cursor assertions may fail if IDs are not coerced to strings.

## Test Plan
- `make check`

## Semver
Patch: tests only.
