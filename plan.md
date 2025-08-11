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
Integrate PHPStan static analysis into the project.

## Constraints
- Add `phpstan/phpstan` as a development dependency.
- Provide `phpstan.neon.dist` with analysis level and paths.
- Update `Makefile` and `release-hygiene.yml` to run `vendor/bin/phpstan analyse`.
- Ensure documentation and tooling references mention PHPStan.

## Risks
- PHPStan may surface existing type errors.
- Docker environments without PHPStan installed will fail `make check`.

## Test Plan
- `vendor/bin/phpstan analyse`
- `bash scripts/agents-verify.sh`
- `make check` (runs formatters, linters, tests, and PHPStan)

## Semver
Patch: development tooling only.
