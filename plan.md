# Plan

## Repo Intake
- Languages: Python, PHP.
- Build tools: setuptools via `pyproject.toml`, Composer for PHP.
- Package managers: pip (requirements.txt), Composer.
- Test commands: `make check` (uses Docker) and `bash scripts/agents-verify.sh`.
- Entry points: `python -m bot.main` for the bot, adapter service via PHP.
- CI jobs: `release-hygiene.yml` and `release.yml`.
- Release process: bump version in `pyproject.toml`, update `CHANGELOG.md`, tag `vX.Y.Z` on main.

## Goal
Enhance `scripts/agents-verify.sh` to ensure tools referenced in `Agents.md` exist and document these checks.

## Constraints
- Verify presence of `docker`, `make check` target, `flake8`, and `phpunit` when mentioned in `Agents.md`.
- Fail the script if any referenced command or file is missing.
- Update `Agents.md` to describe the new verification.
- Bump patch version and changelog.

## Risks
- Missing system dependencies (e.g., Docker daemon) may cause checks to fail.
- Installing required tooling can be slow in CI environments.

## Test Plan
- `bash scripts/agents-verify.sh`
- `make check` (may fail if Docker is unavailable)

## Semver
Patch: CI tooling only.
