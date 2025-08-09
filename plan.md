# Plan

## Goal
Harden session handling by avoiding object serialization and regenerating session IDs in adapter/public/index.php.

## Constraints
- Maintain existing adapter endpoints.
- Use minimal session data (user id, nickname, cookie).

## Risks
- Reconstruction of user from cookie data may fail if library interfaces change.
- Additional disk I/O for cookie storage.

## Test Plan
- Run `php -l adapter/public/index.php`.
- Run `make check` (may fail if Docker unavailable).

## Semver
Patch bump to v0.1.3.
