# AGENTS
**Scope**: Repository operations + release hygiene
**SemVer**: BREAKING/! → MAJOR; feat → MINOR; fix/docs/ci/test/chore → PATCH
**CI commands**: [docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test, docker-compose build, docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"]
**Version files**: [pyproject.toml, composer.json]
**Approvals**: CODEOWNERS define reviewers; at least one maintainer review required
**Security**: `ADAPTER_BASE_URL` must start with `https://`; the bot exits otherwise.

## Workflow Examples
- Audit logs: `/audit search user:123 action:ban`
- Timers: `/timer 10m cleanup`
- Birthdays: `/birthday set 2000-01-01`
- Polls: `/poll create "Best snack?" type:multiple options:"chips;cookies"`
- Moderation: `/warn @user Be nice`
- Welcome: `/welcome setup channel:#introductions message:"Welcome {user}" verify-role:@member`
