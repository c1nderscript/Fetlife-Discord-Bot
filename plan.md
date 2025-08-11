# Plan

## Repo Intake
- Languages: Python, PHP.
- Build tools: setuptools via `pyproject.toml`, Composer for PHP.
- Package managers: pip (requirements.txt), Composer.
- Test commands: `make check` (lint, formatting, unit tests, integration tests) and `bash scripts/agents-verify.sh`.
- Entry points: `python -m bot.main` for the bot, adapter service via PHP.
- CI jobs: `release-hygiene.yml` (make check, version/changelog verification, agents drift check) and `release.yml` (tags and notes).
- Release process: bump version in `pyproject.toml`, update `CHANGELOG.md`, tag `vX.Y.Z` on main.

## Goal
Add Black code formatting and flake8 configuration, provide a fmt target, and ensure check runs Black.

## Constraints
- Configure flake8 to align with Black.
- Add Black dependency to requirements files.
- Update Makefile and developer docs (Agents.md).
- Run formatters and tests via Docker.
- Bump patch version and changelog.

## Risks
- Black reformatting could introduce merge conflicts or stylistic adjustments.
- Requirements lock might drift if not regenerated.

## Test Plan
- `docker compose build` & `make fmt`
- `bash scripts/agents-verify.sh`
- `make check`

## Semver
Patch: tooling and configuration only.
