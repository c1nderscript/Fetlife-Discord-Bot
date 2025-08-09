# Plan

## Goal
Implement adapter polling for subscriptions to fetch events, deduplicate relayed items, update cursors with real IDs, and reschedule with backoff on errors.

## Constraints
- Use existing `adapter_client.fetch_events` for event subscriptions.
- Maintain idempotency by checking `storage.has_relayed` before recording.
- Update cursor with processed item IDs and timestamps.
- Handle HTTP errors gracefully and apply exponential backoff before rescheduling.
- Keep job rescheduling within AsyncIOScheduler.

## Risks
- Missing adapter service or unexpected response shapes may raise runtime errors.
- Backoff logic could starve jobs if errors persist.

## Test Plan
- Unit test successful polling updates cursor and deduplicates relayed items.
- Unit test HTTP errors trigger backoff and reschedule.

## Semver
Minor bump to v0.1.0 for initial feature release.
