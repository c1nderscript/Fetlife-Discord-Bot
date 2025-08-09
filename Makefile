.PHONY: check

check:
	docker compose build
	docker compose run --rm bot flake8 bot
	docker compose run --rm bot pytest
	docker compose run --rm adapter vendor/bin/phpunit
