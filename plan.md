## Repo Intake
- Languages: Python, PHP
- Build tools: setuptools (pyproject), Composer
- Package managers: pip, Composer
- Tests: `bash scripts/agents-verify.sh`, `make fmt`, `make check`
- CI jobs: `release-hygiene.yml`, `release.yml`
- Release process: bump versions in `pyproject.toml` and `composer.json`, update `CHANGELOG.md`, tag `vX.Y.Z`, publish notes from `.github/RELEASE_NOTES.md`

## Goal
Expose PHP package version and document bumping Python and PHP versions together.

## Constraints
- Keep release docs consistent with CI release checks.
- No project version change.

## Risks
- Version drift between Python and PHP packages.
- Incomplete release documentation.

## Test Plan
- `bash scripts/agents-verify.sh`
- `make fmt`
- `make check`

## Semver
No version change (documentation/metadata only) – patch.

## Rollback
Revert this commit.
