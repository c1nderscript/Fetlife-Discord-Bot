## Repo Intake
- Languages: Python, PHP
- Build tools: setuptools, Composer
- Package managers: pip, Composer
- Entrypoints: Docker Compose services `adapter`, `bot`
- Tests: `bash scripts/agents-verify.sh`, `make fmt`, `make check`
- CI jobs: `release-hygiene.yml`, `release.yml`
- Release process: bump versions in `pyproject.toml` and `composer.json`, update `CHANGELOG.md`, tag `vX.Y.Z`, publish notes from `.github/RELEASE_NOTES.md`

## Goal
Ensure adapter service restarts automatically in Docker Compose.

## Constraints
- Follow existing YAML style.
- Bump Python and PHP package versions together.

## Risks
- Docker builds may fail.
- Version bump might drift from other release artifacts.

## Test Plan
- `bash scripts/agents-verify.sh`
- `make fmt`
- `docker compose build`
- `pip-audit`
- `composer audit`
- `make check`

## Semver
Patch release (deployment fix).

## Rollback
Revert this commit.
