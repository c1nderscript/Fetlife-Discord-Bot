## Goal
Clarify deployment instructions for running the bot continuously.

## Constraints
- Keep documentation consistent with scripts and docker-compose configuration.

## Risks
- Inaccurate guidance could lead to failed deployments.

## Test Plan
- `make fmt`
- `make check`
- `bash scripts/agents-verify.sh`

## Semver
Patch release: documentation update.

## Affected Packages
- None

## Rollback
Revert the commit.
