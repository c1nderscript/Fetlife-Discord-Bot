## Goal
Adopt Argon2 hashing for account credentials and migrate existing SHA-256 hashes.

## Constraints
- Follow AGENTS.md: run make fmt and make check before committing.
- Run pip-audit -r requirements.txt and bash scripts/agents-verify.sh.
- Update requirements, Dockerfile, migrations, and docs consistently.

## Risks
- Existing accounts hashed with SHA-256 remain until users log in again.
- Argon2 build dependencies may increase image size.

## Test Plan
- `make fmt`
- `make check`
- `pip-audit -r requirements.txt`
- `bash scripts/agents-verify.sh`

## Semver
Patch release: security hardening.

## Affected Packages
- Python bot (hashing logic and dependencies)
- Alembic migrations
- Documentation

## Rollback
Revert commit and migration; restore SHA-256 hashing.
