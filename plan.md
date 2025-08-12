## Repo Intake
- Languages: Python, PHP
- Build tools: setuptools (pyproject), Composer
- Package managers: pip, Composer
- Tests: `bash scripts/agents-verify.sh`, `make fmt`, `make check`
- CI jobs: `release-hygiene.yml`, `release.yml`
- Release process: bump versions in `pyproject.toml` and `composer.json`, update `CHANGELOG.md`, tag `vX.Y.Z`, publish notes from `.github/RELEASE_NOTES.md`

## Goal
Introduce `CREDENTIAL_SALT` environment variable and use it when hashing credentials.

## Constraints
- Keep hashing backward compatible when salt unset.
- Update docs and examples.

## Risks
- Missing salt could weaken security.
- Incorrect hashing could break account lookups.

## Test Plan
- `bash scripts/agents-verify.sh`
- `make fmt`
- `make check`

## Semver
Patch release (security enhancement, no API change).

## Rollback
Revert this commit.
