# AGENTS
**Scope**: Repository operations + release hygiene  
**SemVer**: BREAKING/! → MAJOR; feat → MINOR; fix/docs/ci/test/chore → PATCH  
**CI commands**: [docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test, docker-compose build, docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"]  
**Version files**: [pyproject.toml, composer.json]  
**Approvals**: CODEOWNERS define reviewers; at least one maintainer review required  
