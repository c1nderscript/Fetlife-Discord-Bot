# Plan

## Repo Intake
- Languages: Python, PHP.
- Build tools: setuptools via `pyproject.toml`, Composer for PHP.
- Package managers: pip (requirements.txt), Composer.
- Test commands: `make check` and `bash scripts/agents-verify.sh`.
- Entry points: `python -m bot.main` for the bot, adapter service via PHP.
- CI jobs: `release-hygiene.yml` and `release.yml`.
- Release process: bump version in `pyproject.toml`, update `CHANGELOG.md`, tag `vX.Y.Z` on main.

## Goal
Create `scripts/install.sh` that collects credentials, writes `.env`, installs dependencies, runs `alembic upgrade head`, and optionally launches Docker Compose. Update documentation to reference the new script.

## Constraints
- Script accepts flags or interactive prompts for required credentials.
- Writes `.env` without overwriting existing keys.
- Installs Python (`pip install -r requirements.txt`) and PHP (`composer install`) dependencies.
- Runs database migrations via `alembic upgrade head`.
- Optional `docker compose up -d` invocation.
- Update `README.markdown` and `Agents.md` to reference the script.
- Bump minor version and changelog entry.

## Risks
- Dependency installation or migrations may fail if tools are missing.
- Docker Compose may not be installed; script must handle absence gracefully.

## Test Plan
- `bash scripts/agents-verify.sh`
- `make fmt` (may fail: docker compose plugin missing)
- `make check` (may fail: docker compose plugin missing)

## Semver
Minor: adds backwards-compatible installation helper.
