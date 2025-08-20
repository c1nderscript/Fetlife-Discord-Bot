All notable changes to this project will be documented here.

## [1.23.2] - 2025-08-20
### Docs
- docs: add monitoring dashboard and alert runbook.

## [1.23.1] - 2025-08-20
### Changed
- fix: use health-aware dependencies and start-first rolling updates in Docker Compose.

## [1.23.0] - 2025-08-20
### Added
- feat: add adapter circuit breaker with Prometheus metric and management UI.

## [1.22.0] - 2025-08-20
### Added
- feat: add correlation ID utility and include IDs in logs.

## [1.21.0] - 2025-08-20
### Added
- feat: expose additional Prometheus metrics for error rates, request latency, queue depth, and Telegram connectivity.

## [1.20.0] - 2025-08-20
### Added
- feat: add configurable retries and intervals for health checks.
### CI
- ci: invoke `make health` in deploy validation workflow.
### Docs
- docs: document health check retry behavior and environment overrides.

## [1.19.1] - 2025-08-20
### CI
- ci: validate adapter HTTPS health and login endpoints with retries in deploy validation script.
### Docs
- docs: document enhanced deploy validation checks.

## [1.19.0] - YYYY-MM-DD
### CI
- ci: introduce health-check scripts and deployment validation workflow.
### Docs
- docs: document health and deploy validation scripts and CI integration.

## [1.18.4] - 2025-08-19
### CI
- ci: add deploy validation workflow and gate pull requests on make health.

## [1.18.3] - 2025-08-19
### CI
- ci: add deployment validation script to verify env vars, database connection, and TLS cert.

## [1.18.2] - 2025-08-19

### CI
- ci: add unified health-check script for bot and adapter endpoints.

## [1.18.1] - 2025-08-19

### Docs
- docs: expand management web interface instructions.

## [1.18.0] - 2025-08-19

### Added
- feat: render management pages with Jinja2 templates.

## [1.17.0] - 2025-08-19

### Added
- feat: add welcome configuration web form with preview option.

## [1.16.0] - 2025-08-19

### Added
- feat: add moderation management forms for warn, mute, kick, ban, timeout, and purge via `/moderation`.

### Docs
- docs: document moderation management forms.

## [1.15.0] - 2025-08-18

### Added
- feat: add management pages for timers and auto-delete settings via `/timers` and `/autodelete`.

### Docs
- docs: document timer and auto-delete management pages.

## [1.14.0] - 2025-08-18

### Added
- feat: implement poll management routes with creation, closing, and results via `/polls`

## [1.13.0] - 2025-08-18

### Added
- feat: expand management web UI with poll, timed message, and welcome pages

### Docs
- docs: add workflow examples for audit logs, timers, birthdays, polls, moderation, and welcome

## [1.12.0] - 2025-08-18

### Added
- Welcome system with `/welcome setup`, configurable messages, optional verification, and join/leave logging.

## [1.11.0] - 2025-08-18

### Added
- Moderation system with `/warn`, `/mute`, `/kick`, `/ban`, `/timeout`, `/modlog`, `/purge`, infractions, escalation, appeals dashboard.

## [1.10.0] - 2025-08-18

### Added
- Polling system with `/poll create`, `/poll close`, `/poll results`, and `/poll list` commands supporting yes/no, multiple choice, and ranked voting with reactions or buttons, auto-close timers, and web UI analytics.

## [1.9.0] - 2025-08-18

### Added
- Birthday reminders with `/birthday` commands, daily scheduler, timezone and privacy options, optional role assignment, and management UI calendar.

## [1.8.0] - 2025-08-18

### Added
- Timed message auto-deletion with `/timer` and `/autodelete` commands, persistent timers, and metrics.

### Docs
- docs(toaster): refresh architecture, core files, deps

## [1.7.0] - 2025-08-18

### Added
- Audit log decorator and `/audit search` command with web UI viewer.

## [1.6.0] - 2025-08-18

### Added
- Rate limit admin commands with configurable per-guild cooldowns.

## [1.5.2] - 2025-08-18

### Added
- Pause polling after repeated adapter failures with `/fl health` status and manual resume.
- Cache events, profiles, and RSVP records during polling.
- Docker healthchecks for bot and adapter services with `make health` helper.
- OpenAPI specification and `/openapi.yaml` route for the adapter.
- Document running the adapter behind an HTTPS reverse proxy and note TLS expectations.
- Index frequent lookup columns for faster database queries.
- Docker-based tests for group posts, messages, and Telegram bridge flows.
- Guild role management commands `/role add`, `/role remove`, and `/role list`.
- Channel management commands `/channel create`, `/channel delete`, and `/channel rename` with permission checks.
- Reaction role mappings with `/reactionrole add` and `/reactionrole remove` plus automatic role application on reactions.
- A management web interface with Discord OAuth2 login for subscriptions, role assignments, and channel settings.

### Changed
- Install Python dependencies from `requirements.lock` for reproducible builds.
- Share an aiohttp `ClientSession` with a default timeout across adapter requests and close it on shutdown.
- Replace `# mypy: ignore-errors` in `bot/storage.py` with explicit type annotations.

### Security
- Run `pip-audit` and `composer audit` in `make check` and release-hygiene workflow.
- Relax root check in `codex.sh` to allow safe commands with a warning and replace `eval` with direct command invocation.
 - Default to HTTPS for `ADAPTER_BASE_URL`, reject non-HTTPS values, and document the requirement with environment variable overrides.

### Fixed
- Validate adapter responses against JSON schemas and relay minimal links on mismatch.
- Exit with clear error when required environment variables are missing.
- Allow importing `bot.main` without triggering environment checks by moving
  initialization into `main()`.

### Docs
- Streamline AGENTS.md with repo-ops skeleton.
- Document branch protections, Conventional Commit requirements, review policy, and security expectations in `.codex-policy.yml` and reference it in contributor guides.
- Define CODEOWNERS for key directories to enforce maintainer reviews.

## [1.3.14] - 2025-08-16
### Security
- Hash account credentials with Argon2id and migrate existing SHA-256 hashes.

## [1.3.13] - 2025-08-16
### Security
- Pin Postgres image to immutable digest in Docker Compose.

## [1.3.12] - 2025-08-16
### Fixed
- Reschedule stored subscriptions on startup so they persist across restarts.

## [1.3.11] - 2025-08-15
### Changed
- Rename `Agents.md` to `AGENTS.md` and update references.
- Clarify deployment steps for Docker Compose and systemd.

## [1.3.10] - 2025-08-15
### Added
- Check that `composer.json` version matches `pyproject.toml` in release-hygiene workflow.
- Prompt for adapter token, base URL, and Telegram API credentials during setup.

## [1.3.9] - 2025-08-14
### Changed
- Provide `.env.example` template with placeholder values and reference it in README and setup script.

## [1.3.8] - 2025-08-14
### Fixed
- Allow bot to run without Telegram credentials.

## [1.3.7] - 2025-08-14
### Changed
- Split development dependencies into `requirements-dev.txt` and update Dockerfile, Makefile, and docs.
## [1.3.6] - 2025-08-12
### Fixed
- Ensure adapter service restarts automatically in Docker Compose.

## [1.3.5] - 2025-08-12
### Fixed
- Pin `flake8` dependency and rebuild bot Docker image.

## [1.3.4] - 2025-08-12
### Added
- Declare PHP package version in `composer.json` and document bumping Python and PHP versions together during releases.
- Salt credential hashes using `CREDENTIAL_SALT` environment variable.
## [1.3.3] - 2025-08-12
### Fixed
- Expose correct bot HTTP port 8000 in Dockerfile.

## [1.3.2] - 2025-08-12
### Changed
- Standardize adapter port to 8000 and document `ADAPTER_BASE_URL`.

## [1.3.1] - 2025-08-12
### Added
- Alembic migration adding `accounts` table and `account_id` foreign key to `subscriptions`.

## [1.3.0] - 2025-08-12
### Added
- `/messages` adapter endpoint and `messages` subscription forwarding DMs to Discord and Telegram.
- Schema, tests, and documentation for message relays.

## [1.2.0] - 2025-08-12
### Added
- Automatic reconnection, attachment forwarding, and `/fl telegram list` command for the Telegram bridge.
### Changed
- Documentation updated to describe enhanced relay behavior.

## [1.1.2] - 2025-08-12
### Added
- Interactive `scripts/install.sh` menu for managing the Python virtual environment.
### Changed
- Documentation updated to reference the new installation workflow.

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
- agents-verify script validates presence of tools referenced in AGENTS.md (docker, make check, flake8, phpunit).


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
