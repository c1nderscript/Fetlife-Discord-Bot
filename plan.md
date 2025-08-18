## Goal
Document audit logs, timers, birthdays, polls, moderation, and welcome workflows with practical examples in README.markdown, AGENTS.md, and toaster.md.

## Constraints
- Follow AGENTS.md: run `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`, `docker-compose build`, and `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"` before committing.
- Run `pip-audit` and `composer audit`.
- Validate with `su nobody -s /bin/bash -c ./codex.sh fast-validate`.

## Risks
- Examples may drift from actual command syntax.
- Documentation could omit security requirements (HTTPS adapter URL).

## Test Plan
- `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`
- `docker-compose build`
- `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"`
- `pip-audit`
- `composer audit`
- `su nobody -s /bin/bash -c ./codex.sh fast-validate`

## Semver
Patch release: documentation-only updates.

## Affected Files
- `README.markdown`
- `AGENTS.md`
- `toaster.md`
- `CHANGELOG.md`
- `plan.md`

## Rollback
Revert commit.
