## Repo Intake
- Languages: Python, PHP
- Build tools: setuptools via `pyproject.toml`, Composer for PHP
- Package managers: pip (requirements.txt), Composer
- Test commands: `make fmt`, `make check`, `bash scripts/agents-verify.sh`
- Entry points: `python -m bot.main` for the bot, adapter service via PHP
- CI jobs: `release-hygiene.yml`, `release.yml`
- Release process: bump version in `pyproject.toml`, update `CHANGELOG.md`, tag `vX.Y.Z`

## Goal
Enhance Telegram relay with automatic reconnection, attachment forwarding, and an `/fl telegram list` command.

## Constraints
- Wrap Telegram client startup and Discord sends in `try/except` with logging.
- Detect Telegram photos/documents and forward as Discord attachments.
- Expose `/fl telegram list` showing active mappings.
- Document the new behavior and bump version metadata.

## Risks
- Media types may not download correctly.
- Reconnection loop could stall tests if misconfigured.

## Test Plan
- `bash scripts/agents-verify.sh`
- `make fmt`
- `make check`

## Semver
Minor: new functionality without breaking existing API (bump to 1.2.0).

## Rollback
Revert the commit and restore previous `TelegramBridge` and command definitions.
