# Plan

## Goal
Add group_posts subscriptions allowing the bot to poll the adapter for group posts and relay them, including target validation.

## Constraints
- Support `sub_type="group_posts"` in `/fl subscribe`.
- Require targets formatted as `group:<id>` where `<id>` is numeric.
- Preserve existing event, writing, and attendee behavior.

## Risks
- Missing validation could allow malformed targets.
- Embed formatting may omit published timestamps.

## Test Plan
- `make check`

## Semver
Minor: new backwards-compatible feature.
