## Goal
Add `.codex-policy.yml` documenting branch protections, Conventional Commit requirements, required reviews, and security expectations. Reference the policy in contributor docs.

## Constraints
- Follow AGENTS.md: run `make fmt` and `make check` before committing.

## Risks
- Policy may drift from actual repository settings.
- Missing documentation links could confuse contributors.

## Test Plan
- `make fmt`
- `make check`
- `rg \.codex-policy.yml -n README.markdown`

## Semver
Patch release: documentation only.

## Affected Packages
- Documentation

## Rollback
Revert the commits and remove `.codex-policy.yml` and related README and CHANGELOG entries.
