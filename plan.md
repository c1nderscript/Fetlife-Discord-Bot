## Repo Intake
- Languages: Python, PHP
- Build tools: setuptools via `pyproject.toml`, Composer for PHP
- Package managers: pip (requirements.txt), Composer
- Test commands: `make fmt`, `make check`, `bash scripts/agents-verify.sh`
- Entry points: `python -m bot.main` for the bot, adapter service via PHP
- CI jobs: `release-hygiene.yml`, `release.yml`
- Release process: bump version in `pyproject.toml`, update `CHANGELOG.md`, tag `vX.Y.Z`

## Goal
Add Alembic migration `0002_add_accounts` creating the `accounts` table and linking it to `subscriptions` via `account_id`.

## Constraints
- Preserve existing subscription data; new `account_id` column must be nullable.

## Risks
- Migration may fail if schemas drift from models.
- Inconsistent foreign key constraints could break subscription queries.

## Test Plan
- `bash scripts/agents-verify.sh`
- `make fmt`
- `make check`
- `alembic upgrade head`

## Semver
Patch: adds missing database structures without altering external APIs (bump to 1.3.1).

## Rollback
Revert the commit and downgrade the database via Alembic to drop the new table and column.
