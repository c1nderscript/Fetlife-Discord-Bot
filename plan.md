## Repo Intake
- Languages: Python, PHP
- Build tools: setuptools via `pyproject.toml`, Composer for PHP
- Package managers: pip (requirements.txt), Composer
- Test commands: `make fmt`, `make check`, `bash scripts/agents-verify.sh`
- Entry points: `python -m bot.main` for the bot, adapter service via PHP
- CI jobs: `release-hygiene.yml`, `release.yml`
- Release process: bump version in `pyproject.toml`, update `CHANGELOG.md`, tag `vX.Y.Z`

## Goal
Unify the adapter and documentation on port 8000 and surface `ADAPTER_BASE_URL` in configuration templates.

## Constraints
- Preserve existing service wiring and avoid conflicting with bot port usage.

## Risks
- Overlooked references to the old port could break connectivity.

## Test Plan
- `bash scripts/agents-verify.sh`
- `make fmt`
- `make check`

## Semver
Patch: documentation and configuration fixes without API changes (bump to 1.3.2).

## Rollback
Revert the commit and restore previous port references.
