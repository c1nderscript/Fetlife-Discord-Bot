## Goal
Replace inline HTML management pages with Jinja2 templates and verify rendering.

## Constraints
- Follow AGENTS.md: run `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`, `docker-compose build`, and `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"` before committing.
- Run `pip-audit` and `composer audit`.
- Validate with `su nobody -s /bin/bash -c ./codex.sh fast-validate`.

## Risks
- Template paths misconfigured leading to runtime errors.
- Tests may rely on previous inline HTML structure.
- Unescaped input could allow HTML injection.

## Test Plan
- `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`
- `docker-compose build`
- `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"`
- `pip-audit`
- `composer audit`
- `su nobody -s /bin/bash -c ./codex.sh fast-validate`

## Semver
Minor release: add Jinja2-templated management web interface.

## Affected Files
- `bot/main.py`
- `bot/templates/*`
- `bot/tests/test_web_interface.py`
- `requirements.txt`
- `requirements.lock`
- `README.markdown`
- `CHANGELOG.md`
- `pyproject.toml`
- `composer.json`
- `plan.md`

## Rollback
Revert commit.
