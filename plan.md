## Repo Intake
- Languages: Python, PHP
- Build tools: setuptools via `pyproject.toml`, Composer for PHP
- Package managers: pip (requirements.txt), Composer
- Test commands: `make fmt`, `make check`, `bash scripts/agents-verify.sh`
- Entry points: `python -m bot.main` for the bot, adapter service via PHP
- CI jobs: `release-hygiene.yml`, `release.yml`
- Release process: bump version in `pyproject.toml`, update `CHANGELOG.md`, tag `vX.Y.Z`

## Goal
Add interactive installer menu for managing the Python virtual environment.

## Constraints
- Provide Install, Reinstall, Uninstall, and Exit options
- Warn before deleting an existing `.venv`
- Ensure `.venv/` is ignored by git
- Update documentation, version metadata, and changelog

## Risks
- Accidental removal of a developer's environment
- Documentation drift if references are missed

## Test Plan
- `bash scripts/agents-verify.sh`
- `make fmt`
- `make check`

## Semver
Patch: tooling enhancement without API changes

## Rollback
Revert the commit and restore previous `scripts/install.sh`
