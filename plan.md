## Repo Intake
- Languages: Python, PHP
- Build tools: setuptools (pyproject), Composer
- Package managers: pip, Composer
- Tests: `bash scripts/agents-verify.sh`, `make fmt`, `make check`
- Entrypoints: `python -m bot.main`, adapter via PHP
- CI jobs: `release-hygiene.yml`, `release.yml`
- Release process: bump version in `pyproject.toml`, update `CHANGELOG.md`, tag `vX.Y.Z`

## Goal
Expose the bot's HTTP server on port 8000 in the Docker image.

## Constraints
- Do not alter runtime behavior beyond the Dockerfile port.
- Preserve existing build and release tooling.

## Risks
- Missing version bump or changelog entry could lead to release drift.

## Test Plan
- `bash scripts/agents-verify.sh`
- `make fmt`
- `make check`
- `docker build -t bot-test -f bot/Dockerfile .`
- `docker run --rm -d -p 8000:8000 -e DISCORD_TOKEN=dummy --name bot-test bot-test`
- `curl -f http://localhost:8000/metrics`
- `curl -f http://localhost:8000/ready || true` (expected 503 without Discord connectivity)

## Semver
Patch bump to 1.3.3.

## Rollback
Revert the commit and rebuild the previous Docker image.
