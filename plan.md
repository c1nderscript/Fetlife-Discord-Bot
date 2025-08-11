# Plan

## Goal
Document how to run the bot 24/7 on a remote server in README.

## Constraints
- Include Docker Compose and systemd options.
- Reference `scripts/setup.sh` for initial configuration.
- Mention log locations and service status commands.
- Follow repository documentation and release conventions.

## Risks
- `systemd` paths differ across distributions.
- Inaccurate log paths could mislead users.

## Test Plan
- `bash scripts/agents-verify.sh`
- `make check`

## Semver
Patch: documentation-only change.
