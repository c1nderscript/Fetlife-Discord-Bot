# Plan

## Repo Intake
- Languages: Python, PHP.
- Build tools: setuptools via `pyproject.toml`, Composer for PHP.
- Package managers: pip (requirements.txt), Composer.
- Test commands: `make check` (uses Docker) and `bash scripts/agents-verify.sh`.
- Entry points: `python -m bot.main` for the bot, adapter service via PHP.
- CI jobs: `release-hygiene.yml` and `release.yml`.
- Release process: bump version in `pyproject.toml`, update `CHANGELOG.md`, tag `vX.Y.Z` on main.

## Goal
Require a shared token for adapter requests using middleware, configured via `ADAPTER_AUTH_TOKEN`, and document the setup.

## Constraints
- Middleware in `adapter/public/index.php` must enforce `Authorization: Bearer <token>` from `ADAPTER_AUTH_TOKEN`.
- Requests with missing/invalid token return HTTP 401.
- Update adapter client to send the token from environment variable.
- Include token variable in Docker Compose, `.env.example`, README, and Agents spec.
- Bump version and changelog; add decision log entry.

## Risks
- Existing deployments without token will fail to authenticate.
- Token leakage in logs or configs could expose adapter.

## Test Plan
- `bash scripts/agents-verify.sh`
- `pytest bot/tests/test_adapter_client.py::test_auth_header`
- `make check` (may fail if Docker is unavailable)

## Semver
Major: adapter API now requires authentication.
