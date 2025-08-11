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
Add mypy static type checking for the `bot` package and integrate it into the development workflow.

## Constraints
- Add mypy and required type stubs to requirements files.
- Configure mypy in `pyproject.toml` targeting `bot/`.
- Update Makefile and developer docs (Agents.md).
- Resolve existing type errors.
- Bump patch version and changelog.

## Risks
- Missing type stubs for dependencies may require ignores.
- Requirements lock might drift if not regenerated.

## Test Plan
- `docker compose build`
- `bash scripts/agents-verify.sh`
- `make fmt`
- `make check`

## Semver
Patch: tooling and typing only.
