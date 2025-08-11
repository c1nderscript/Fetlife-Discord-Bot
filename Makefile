.PHONY: check fmt

fmt:
	docker compose run --rm bot black bot

check:
	docker compose build
	docker compose run --rm bot black --check bot
	docker compose run --rm bot flake8 bot
	docker compose run --rm bot mypy bot
	docker compose run --rm bot pytest
	docker compose -f tests/docker-compose.test.yml build
	docker compose -f tests/docker-compose.test.yml run --rm bot-test
	docker compose -f tests/docker-compose.test.yml down || true
	docker compose run --rm adapter vendor/bin/phpunit
