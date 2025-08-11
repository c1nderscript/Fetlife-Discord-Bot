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
Convert Dockerfiles to multi-stage builds with pinned base image digests and document the rationale.

## Constraints
- `adapter/Dockerfile` and `bot/Dockerfile` use multi-stage builds.
- Final stages contain only runtime dependencies and application code.
- Pin base images: `php:8.2-cli@sha256:304cfb487bbe9b2ce5a933f6e5848e0248bff1fbb0d5ee36cec845f4a34f4fb1` and `python:3.11-slim@sha256:0ce77749ac83174a31d5e107ce0cfa6b28a2fd6b0615e029d9d84b39c48976ee`.
- Update `Agents.md` with pinned versions and build rationale.
- Bump version and changelog; add decision log entry.

## Risks
- Pinned digests require manual updates for upstream security fixes.
- Missing runtime tools if build-stage packages are omitted.

## Test Plan
- `bash scripts/agents-verify.sh`
- `make fmt` (fails: docker compose plugin missing)
- `make check` (fails: docker compose plugin missing)
- `pytest bot/tests/test_adapter_client.py::test_auth_header`

## Semver
Patch: build changes only.
