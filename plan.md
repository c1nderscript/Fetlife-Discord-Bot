## Repo Intake
- Languages: Python, PHP
- Build tools: setuptools via `pyproject.toml`, Composer for PHP
- Package managers: pip (requirements.txt), Composer
- Test commands: `make fmt`, `make check`, `bash scripts/agents-verify.sh`
- Entry points: `python -m bot.main` for the bot, adapter service via PHP
- CI jobs: `release-hygiene.yml`, `release.yml`
- Release process: bump version in `pyproject.toml`, update `CHANGELOG.md`, tag `vX.Y.Z`

## Goal
Add `messages` subscription relaying direct messages to Discord and Telegram via a new adapter `/messages` endpoint.

## Constraints
- Adapter must reuse existing authenticated session.
- Store cursors per subscription to avoid duplicate DMs.
- Forward DMs to mapped Telegram chats when configured.
- Update docs, schemas, and configuration to reflect new subscription type.

## Risks
- Parsing FetLife messages may break if page layout changes.
- Telegram send failures could drop DMs silently.

## Test Plan
- `bash scripts/agents-verify.sh`
- `make fmt`
- `make check`

## Semver
Minor: new functionality without breaking existing API (bump to 1.3.0).

## Rollback
Revert the commit and remove `messages` subscription and adapter endpoint.
