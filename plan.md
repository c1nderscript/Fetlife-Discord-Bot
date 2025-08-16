## Goal
Document how to run the adapter behind an HTTPS reverse proxy and note TLS expectations in the development spec.

## Constraints
- Follow AGENTS.md: run `make fmt` and `make check` before committing.
- Update README.markdown, AGENTS.md, and CHANGELOG.md.

## Risks
- Misconfigured proxy headers could break authentication.
- Inconsistent documentation may confuse deployers.

## Test Plan
- `make fmt`
- `make check`

## Semver
Patch release: documentation-only changes.

## Affected Packages
- Documentation

## Rollback
Revert the commit to remove documentation changes.
