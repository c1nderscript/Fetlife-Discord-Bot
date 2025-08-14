.PHONY: check fmt

fmt:
	docker compose run --rm bot sh -c "pip install -r requirements-dev.txt && black bot"

check:
	docker compose build
	docker compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot && pytest"
	docker compose -f tests/docker-compose.test.yml build
	docker compose -f tests/docker-compose.test.yml run --rm bot-test
	docker compose -f tests/docker-compose.test.yml down || true
	docker compose run --rm adapter vendor/bin/phpunit
