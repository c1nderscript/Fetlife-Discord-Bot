## Goal
Add polling system with `/poll create`, `/poll close`, `/poll results`, and `/poll list` commands supporting yes/no, multiple choice, and ranked voting with reaction or button inputs, auto-close timers, and analytics in the web UI.

## Constraints
- Follow AGENTS.md: run `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`, `docker-compose build`, and `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"` before committing.
- Run `pip-audit` and `composer audit`.
- Validate with `su nobody -s /bin/bash -c ./codex.sh fast-validate`.

## Risks
- Concurrency issues could allow multiple votes per user if reactions aren't properly tracked.
- Ranked-choice tallying may be miscomputed leading to incorrect results.
- Auto-close timers might fail if the bot restarts before completion.

## Test Plan
- `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`
- `docker-compose build`
- `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"`
- `pip-audit`
- `composer audit`
- `su nobody -s /bin/bash -c ./codex.sh fast-validate`

## Semver
Minor release: adds new feature without breaking existing APIs.

## Affected Packages
- `bot/polling.py`
- `bot/main.py`
- `README.markdown`
- `toaster.md`
- `CHANGELOG.md`
- `pyproject.toml`
- `composer.json`

## Rollback
Revert commit.
