## Goal
Rename `Agents.md` to `AGENTS.md` and update all references.

## Constraints
- Keep scripts, CI configs, and docs in sync with the new filename.
- Preserve existing drift-check behaviour.

## Risks
- Missing a reference could break verification or documentation links.

## Test Plan
- `bash scripts/agents-verify.sh`

## Semver
Patch release: documentation and tooling reference update.

## Affected Packages
- None

## Rollback
Revert the commit.
