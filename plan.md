# Plan

## Goal
Support attendee subscriptions by adding adapter endpoint `/events/{id}/attendees` and bot polling that relays attendee RSVP statuses and comments into Discord.

## Constraints
- Keep existing adapter service patterns and reuse session/account handling.
- Responses must include attendee `id`, `nickname`, `status`, and optional `comment`.
- Maintain backward compatibility for existing event and writing subscriptions.

## Risks
- Parsing attendee lists may be slow and fail if HTML structure changes.
- Schema or embed formatting errors could break polling.

## Test Plan
- `make check`

## Semver
Minor: new backwards-compatible feature.
