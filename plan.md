## Repo Intake
- Languages: Python, PHP
- Build tools: setuptools (pyproject), Composer
- Package managers: pip, Composer
- Tests: `bash scripts/agents-verify.sh`, `make fmt`, `make check`
- CI jobs: `release-hygiene.yml`, `release.yml`
- Release process: bump version in `pyproject.toml`, update `CHANGELOG.md`, tag `vX.Y.Z`

## Goal
Append release notes for v0.9.0–v1.3.0 and confirm release workflow references them.

## Constraints
- Follow existing release note style.
- No version bump or changelog updates.

## Risks
- Misaligned release summaries.

## Test Plan
- `bash scripts/agents-verify.sh`
- `make fmt`
- `make check`

## Semver
No version change (documentation only).

## Rollback
Revert this commit.
