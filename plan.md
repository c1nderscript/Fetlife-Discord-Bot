# Plan

## Goal
Add a commit-msg git hook enforcing Conventional Commits and document installation steps for contributors.

## Constraints
- Hook must validate commit messages against Conventional Commits regex.
- Instructions belong in Agents.md per repository guidelines.
- Maintain changelog entry without releasing a new version.

## Risks
- Contributors may skip installing the hook and experience commit failures later.
- Hook script may not be portable across all shells.

## Test Plan
- `make check`
- `scripts/agents-verify.sh`

## Semver
Patch; documentation and tooling only.
