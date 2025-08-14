## Repo Intake
- Languages: Python, PHP
- Build tools: setuptools, Composer
- Package managers: pip, Composer
- Entrypoints: Docker Compose services `adapter`, `bot`
- Tests: `bash scripts/agents-verify.sh`, `make fmt`, `make check`
- CI jobs: `release-hygiene.yml`, `release.yml`
- Release process: bump versions in `pyproject.toml` and `composer.json`, update `CHANGELOG.md`, tag `vX.Y.Z`, publish notes from `.github/RELEASE_NOTES.md`

## Goal
Split development dependencies from runtime and ensure tooling installs dev extras only when needed.

## Constraints
- Follow existing file styles.
- Bump Python and PHP package versions together.

## Risks
- Missing dev dependencies could break formatting or tests.
- Documentation may drift from new dependency layout.

## Test Plan
- `bash scripts/agents-verify.sh`
- `make fmt`
- `pip-audit -r requirements.txt -r requirements-dev.txt`
- `composer audit`
- `make check`

## Semver
Patch release (build workflow change).

## Rollback
Revert this commit.
