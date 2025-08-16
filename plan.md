## Goal
Install Python dependencies from requirements.lock in Docker build and install script, and document lock usage.

## Constraints
- Follow AGENTS.md: run `make fmt` and `make check` before committing.
- Update `bot/Dockerfile` and `scripts/install.sh` to use `requirements.lock`.
- Document lock file usage in `AGENTS.md` and `CHANGELOG.md`.

## Risks
- Outdated lock file may cause installation failures.
- Divergence between `requirements.lock` and requirements files could break builds.

## Test Plan
- `make fmt`
- `make check`

## Semver
Patch release: build and documentation changes only.

## Affected Packages
- Python bot

## Rollback
Revert commit to restore previous installation behavior.
