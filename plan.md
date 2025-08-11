# Plan

## Goal
Implement adapter authentication verification via `/fl login` command using a new helper.

## Constraints
- Use aiohttp for HTTP requests.
- Follow existing command structure and metrics rate limiting.
- Maintain documentation and tests in sync with behavior.

## Risks
- Network errors during adapter login could produce unclear user feedback.
- Misreported status if adapter returns unexpected codes.

## Test Plan
- `make check`

## Semver
Patch: fixes `/fl login` to verify adapter authentication.
