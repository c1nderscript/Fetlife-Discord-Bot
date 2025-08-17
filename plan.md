## Goal
Replace deprecated `docker-compose` commands with the modern `docker compose` CLI and document the change.

## Constraints
- Follow AGENTS.md: run `make fmt` and `make check` before committing.
- Update README and CHANGELOG.md to reference the new CLI.

## Risks
- Environments without the Docker Compose plugin will fail to run Makefile targets.
- Command flag differences could break developer workflows.

## Test Plan
- `make fmt`
- `make check`

## Semver
Patch release: docs and tooling update.

## Affected Packages
- Makefile
- Documentation

## Rollback
Revert the commit to restore previous Compose commands.
