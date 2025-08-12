## Repo Intake
- Languages: Python, PHP
- Build tools: setuptools via `pyproject.toml`, Composer for PHP
- Package managers: pip (requirements.txt), Composer
- Test commands: `make fmt`, `make check`, `bash scripts/agents-verify.sh`
- Entry points: `python -m bot.main` for the bot, adapter service via PHP
- CI jobs: `release-hygiene.yml`, `release.yml`
- Release process: bump version in `pyproject.toml`, update `CHANGELOG.md`, tag `vX.Y.Z`

## Goal
Restrict admin-level commands to administrators, add error handling, and test unauthorized access.

## Constraints
- Apply `@app_commands.default_permissions(administrator=True)` to admin commands
- Wrap command bodies with try/except and respond `ephemeral=True` on errors
- Add unit tests for unauthorized access attempts
- Update version metadata and changelog
- Follow Conventional Commits

## Risks
- Permission checks may bypass tests
- Error handling might hide underlying issues

## Test Plan
- `bash scripts/agents-verify.sh`
- `make fmt`
- `make check`

## Semver
Patch: backward-compatible permission enforcement and tests
