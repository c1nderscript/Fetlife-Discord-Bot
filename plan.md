# Plan

## Repo Intake
- Languages: Python, PHP.
- Build tools: setuptools via `pyproject.toml`, Composer for PHP.
- Package managers: pip (requirements.txt), Composer.
- Test commands: `make check` (lint, unit tests, integration tests) and `bash scripts/agents-verify.sh`.
- Entry points: `python -m bot.main` for the bot, adapter service via PHP.
- CI jobs: `release-hygiene.yml` (make check, version/changelog verification, agents drift check) and `release.yml` (tags and notes).
- Release process: bump version in `pyproject.toml`, update `CHANGELOG.md`, tag `vX.Y.Z` on main.

## Goal
Switch bot execution to module invocation and update all references from `python bot/main.py` to `python -m bot.main`.

## Constraints
- Update `docker-compose.yml`, `bot/Dockerfile`, `scripts/setup.sh`, and documentation.
- Preserve commit conventions and run repository checks.
- Bump patch version and changelog.

## Risks
- Missing environment variables may cause startup failure when verifying.
- Potential overlooked references to old command.

## Test Plan
- `bash scripts/agents-verify.sh`
- `make check`
- `python -m bot.main` (expect failure without token but confirms entry point)

## Semver
Patch: command and documentation adjustments only.
