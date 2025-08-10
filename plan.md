# Plan

## Goal
Add CI workflows for release hygiene and automated tagging.

## Constraints
- release-hygiene must run `make check`, verify `pyproject.toml` version against `CHANGELOG.md`, and run AGENTS drift script.
- release workflow tags releases from main and publishes notes.
- Follow semantic versioning and Keep a Changelog.

## Risks
- `make check` may fail due to missing Docker or dependencies.
- Tag creation can fail if the tag already exists.

## Test Plan
- `make check`
- `scripts/agents-verify.sh`

## Semver
Patch bump to v0.1.6.
