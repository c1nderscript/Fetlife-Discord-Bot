# Plan

## Goal
Provide an interactive setup script that writes required environment variables, applies database migrations, and launches the bot. Update documentation to reference the new script.

## Constraints
- Bash script must skip existing `.env` entries.
- Support optional creation of `config.yaml`.
- Adhere to repository release and documentation conventions.

## Risks
- Script may fail if dependencies like Alembic or Docker are missing.
- Writing to existing files could overwrite user configuration.

## Test Plan
- `bash scripts/agents-verify.sh`
- `make check`

## Semver
Minor: adds a new setup feature.
