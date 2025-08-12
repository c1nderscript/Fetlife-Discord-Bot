# Changelog
All notable changes to this project will be documented here.

## [Unreleased]

## [1.1.1] - 2025-08-12
### Changed
- Restrict admin-level commands to administrators with error handling.
### Added
- Unit tests for unauthorized command access.

## [1.1.0] - 2025-08-12
### Added
- `scripts/install.sh` to configure environment, install dependencies, run migrations, and optionally start Docker Compose.
### Changed
- README instructions now reference `scripts/install.sh`.

## [1.0.1] - 2025-08-11
### Changed
- Convert adapter and bot Dockerfiles to multi-stage builds with pinned base image digests.


## [1.0.0] - 2025-08-11
### Added
- Token-based adapter authentication via `ADAPTER_AUTH_TOKEN`.

## [0.8.4] - 2025-08-11
### Added
- agents-verify script validates presence of tools referenced in Agents.md (docker, make check, flake8, phpunit).


## [0.8.3] - 2025-08-11
### Added
- MyPy static type checking and integration into `make check`.

## [0.8.2] - 2025-08-11
### Added
- Black code formatting configuration and `make fmt` target.
### Changed
- `make check` now runs `black --check`.

## [0.8.1] - 2025-08-11
### Added
- Instructions for running the bot 24/7 on a remote server using Docker Compose or systemd.
### Changed
- Run bot as a module via `python -m bot.main` in Docker and documentation.

## [0.8.0] - 2025-08-11
### Added
- Interactive setup script for environment configuration, migrations, and bot startup.

## [0.7.1] - 2025-08-11
### Fixed
- `/fl login` now verifies adapter authentication and reports failures.

## [0.7.0] - 2025-08-11
### Added
- Relay Telegram chats into Discord with a Telethon bridge and `/fl telegram` commands.

## [0.6.0] - 2025-08-11
### Added
- Subscribe to group posts with `/fl subscribe group_posts group:<id>` and relay new posts.

## [0.5.0] - 2025-08-11
### Added
- Adapter endpoint `/events/{id}/attendees` returning RSVP status and comments.
- Bot support for `attendees` subscriptions with embedded RSVP notifications.

## [0.4.0] - 2025-08-11
### Added
- Manage multiple FetLife accounts with `/fl account` subcommands and optional per-subscription selection.
- Adapter and bot polling now isolate sessions per account via `X-Account-ID` header.
- Database models and storage helpers for accounts with hashed credentials.
- Tests covering account creation, selection, and multi-account polling.

## [0.3.2] - 2025-08-11
### Added
- Test verifying writings subscription updates the cursor and sends a message.

## [0.3.1] - 2025-08-11
### Fixed
- Constrain subscription type to events or writings, clarify target formats, and schedule polling with stored type.

## [0.3.0] - 2025-08-11
### Added
- Relay events and user writings as Discord embeds during polling.

## [0.2.0] - 2025-08-11
### Added
- Adapter client helpers for fetching user writings and group posts.

## [0.1.8] - 2025-08-11
### Fixed
- Clean up temporary cookie files after login and during tests.
### Added
- PHPUnit test ensuring cookie file removal.

## [0.1.7] - 2025-08-10
### Added
- commit-msg git hook enforcing Conventional Commits with installation instructions.
### Fixed
- Return informative error when subscription filters contain invalid JSON.

## [0.1.6] - 2025-08-10
### Added
- CI release-hygiene workflow running make check, version/changelog verification, and Agents drift check.
- Release workflow tagging main and publishing notes.

## [0.1.5] - 2025-08-10
### Added
- AGPL-3.0-or-later license file and references in README and package metadata.

## [0.1.4] - 2025-08-09
### Added
- Docker-based integration test harness for subscribe flow.

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
