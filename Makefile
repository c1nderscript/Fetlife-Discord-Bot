.PHONY: check fmt health

fmt:
	docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black bot"

check:
	docker-compose build
	docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && pip-audit && black --check bot && flake8 bot && mypy bot && pytest"
	docker-compose -f tests/docker-compose.test.yml build
	docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test
	docker-compose -f tests/docker-compose.test.yml down || true
	docker run --rm -v $(PWD):/app composer audit
	docker-compose run --rm adapter vendor/bin/phpunit

health:
	docker-compose exec bot curl -f http://localhost:8000/ready
	docker-compose exec adapter curl -f http://localhost:8000/healthz
