## Repo Intake
- Languages: Python, PHP
- Build tools: setuptools via `pyproject.toml`, Composer for PHP
- Package managers: pip (requirements.txt), Composer
- Test commands: `make fmt`, `make check`, `bash scripts/agents-verify.sh`
- Entry points: `python -m bot.main`, adapter service via PHP
- CI jobs: `release-hygiene.yml`, `release.yml`
- Release process: bump version in `pyproject.toml`, update `CHANGELOG.md`, tag `vX.Y.Z`

## Goal
Ignore local virtual environment and document its location.

## Constraints
- Append `.venv/` to `.gitignore`
- Document `.venv/` as standard virtual environment path in `Agents.md` and `README.markdown`
- Bump version metadata and changelog
- Follow semantic commits

## Risks
- Developers using different virtual environment paths may create inconsistencies

## Test Plan
- `bash scripts/agents-verify.sh`
- `make fmt`
- `make check`

## Semver
Patch: documentation and gitignore update

## Affected Packages
- root package

## Rollback
- Revert commit and restore previous version and changelog entry
