## Goal
Pin Postgres image digest in Docker Compose and document the change.

## Constraints
- Follow AGENTS.md: run make fmt and make check before committing.
- Run pip-audit and agents-verify.
- Keep versioning and changelog consistent.

## Risks
- Digest may become outdated, requiring refreshes.

## Test Plan
- `make fmt`
- `make check`
- `pip-audit -r requirements.txt`
- `bash scripts/agents-verify.sh`

## Semver
Patch release: security hardening.

## Affected Packages
- Docker Compose configuration (db service)
- Python bot
- PHP adapter (version bump only)

## Rollback
Revert commit and reset versions and digest.
