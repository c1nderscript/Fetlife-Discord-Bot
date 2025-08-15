<!-- Release notes will be compiled here for each tagged version. -->

## v1.3.9
- Provide `.env.example` template with placeholder values and reference it in README and setup script.

## v1.3.8
- Allow bot to run without Telegram credentials.

## v1.3.7
- Split development dependencies into `requirements-dev.txt` and update Dockerfile, Makefile, and docs.

## v1.3.6
- Ensure adapter service restarts automatically in Docker Compose.

## v1.3.5
- Pin `flake8` dependency and rebuild bot Docker image.

## v1.3.4
- Declare PHP package version in `composer.json` and document bumping Python and PHP versions together during releases.
- Salt credential hashes using `CREDENTIAL_SALT` environment variable.

## v1.3.3
- Expose correct bot HTTP port 8000 in Dockerfile.

## v1.3.2
- Standardize adapter port to 8000 and document `ADAPTER_BASE_URL`.

## v1.3.1
- Alembic migration adding `accounts` table and `account_id` foreign key to `subscriptions`.

## v1.3.0
- `/messages` adapter endpoint with DM forwarding to Discord and Telegram.
- Schema, tests, and docs for message relays.

## v1.2.0
- Automatic reconnection, attachment forwarding, and `/fl telegram list` for the Telegram bridge.
- Docs updated for enhanced relay behavior.

## v1.1.0
- `scripts/install.sh` for environment setup, dependency installation, migrations, and optional Docker Compose start.
- README now references `scripts/install.sh`.

## v1.0.0
- Token-based adapter authentication via `ADAPTER_AUTH_TOKEN`.

## v0.9.0
- Development tooling: 24/7 run instructions, Black formatting + `make fmt`, MyPy checks, and `agents-verify` script.

## v0.8.0
- Add interactive setup script for environment configuration and migrations.

## v0.6.0
- Add group post subscriptions with target validation and relay.
