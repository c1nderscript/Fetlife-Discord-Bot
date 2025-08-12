## Repo Intake
- Languages: Python, PHP
- Build tools: setuptools, Composer
- Package managers: pip, Composer
- Tests: `bash scripts/agents-verify.sh`, `make fmt`, `make check`
- CI jobs: `release-hygiene.yml`, `release.yml`
- Release process: bump versions in `pyproject.toml` and `composer.json`, update `CHANGELOG.md`, tag `vX.Y.Z`, publish notes from `.github/RELEASE_NOTES.md`

## Goal
Pin `flake8` in `requirements.txt` and rebuild the bot Docker image, updating lockfiles as needed.

## Constraints
- Keep dependency versions pinned.
- Update lock files to reflect added dependency.
- Rebuild bot Docker image with updated requirements.

## Risks
- Dependency resolution may modify other packages unexpectedly.
- Docker build could fail if requirements conflict.

## Test Plan
- `bash scripts/agents-verify.sh`
- `make fmt`
- `docker compose build bot`
- `make check`

## Semver
Patch release (development tooling update).

## Rollback
Revert this commit.
