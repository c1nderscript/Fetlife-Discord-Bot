# Changelog
All notable changes to this project will be documented here.

## [Unreleased]

## [0.1.3] - 2025-08-09
### Security
- Store only session tokens instead of serialized objects and regenerate session IDs after login.

## [0.1.2] - 2025-08-09
### Changed
- Pin Python and PHP dependency versions.

## [0.1.1] - 2025-08-09
### Fixed
- Add imports so tests run standalone without path issues.

## [0.1.0] - 2025-08-09
### Added
- Poll adapter for events, deduplicate relays, update cursors, and apply backoff on errors.
