# toaster.md — Fetlife-Discord-Bot (v1.28.5)

**TL;DR:** Discord bot and PHP adapter that relay FetLife activity into chat channels.  
Each major directory now includes an `AGENTS.md` describing its purpose and key files.
**Primary runtime(s):** Python 3.11 & PHP 8.2 · **Targets:** bot, adapter services · **Owner(s):** @c1nderscript @raincoats  
**Last refreshed:** 2025-08-22 09:25 UTC

## System Overview
Python bot polls a FetLife adapter service, persists state in PostgreSQL, and forwards updates to Discord and optional Telegram chats. Adapter calls use a circuit breaker for graceful degradation.
```mermaid
flowchart LR
  U[User/Caller] --> E[Entrypoint: bot/main.py]
  E --> M1[adapter_client]
  E --> M2[discord/telegram handlers]
  M1 --> DS[(PostgreSQL)]
  M2 --> EXT{FetLife & Discord APIs}
  subgraph Ops
    CI[CI/CD] --> Test
    CI --> Build
  end
```
*Legend:* rectangles = code modules; cylinders = data stores; hex = external services; subgraph Ops = pipeline.

## Core Files & Directories

| Path | Role | Why it matters | Notable funcs/classes |
| --- | --- | --- | --- |
| bot/main.py | Discord bot entrypoint | Initializes scheduler, commands, and web server | `FLBot`, `main()` |
| bot/config.py | YAML and env config loader | Centralizes configuration overrides | `load_config`, `get_channel_config` |
| bot/adapter_client.py | HTTP client for adapter service | Validates adapter responses and handles auth | `_get_session`, `fetch_events` |
| bot/db.py | Database URL builder and engine setup | Provides SQLAlchemy session and credential hashing | `SessionLocal`, `hash_credentials` |
| bot/models.py | ORM models | Defines tables for guilds, channels, accounts, subscriptions | `Guild`, `Subscription` |
| bot/storage.py | Subscription and account persistence helpers | Manage subscriptions and FetLife accounts | `add_subscription`, `list_accounts` |
| bot/rate_limit.py | Async token bucket rate limiter | Throttles admin commands | `TokenBucket` |
| bot/tasks.py | Background cleanup tasks | Deletes expired timed messages | `delete_expired_messages` |
| bot/telegram_bridge.py | Telegram integration | Bridges messages between Discord and Telegram | `TelegramBridge` |
| bot/audit.py | Audit logging decorator | Records management actions to DB | `log_action` |
| bot/moderation.py | Moderation helpers and infractions model | Records infractions and appeals | `Infraction` |
| bot/welcome.py | Welcome messages and verification | Sends welcome messages and verifies members | `WelcomeConfig` |
| bot/utils.py | Misc helpers | Shared utility functions | `parse_filters` |
| bot/birthday.py | Birthday reminders and scheduler | Stores birthdays and announces them daily | `Birthday`, `schedule` |
| bot/polling.py | Poll models and helpers | Stores polls and votes and schedules auto-close timers | `Poll`, `PollVote` |
| adapter/public/index.php | Adapter HTTP entrypoint | Exposes FetLife scraping functions over HTTP | Slim `App`, `metric_inc` |
| adapter/openapi.yaml | Adapter API spec | Documents adapter endpoints | OpenAPI definitions |
| src/Connection.php | PHP client for FetLife | Handles session and CSRF management | `Connection` |
| src/User.php | PHP user model | Represents FetLife user data | `User` |
| src/Event.php | PHP event model | Represents FetLife events | `Event` |
| docker-compose.yml | Orchestrates services | Runs bot, adapter, and Postgres together | service definitions |
| .env.example | Environment template | Lists required keys and defaults | env placeholders |
| alembic/ | Database migrations | Tracks schema changes | revision files |
| schemas/ | JSON schemas for adapter | Validates adapter responses | `event.json`, `message.json` |
| .github/workflows/release-hygiene.yml | CI workflow | Runs lint, tests, security audits | GitHub Actions jobs |
| codex.sh | Ops helper script | Safe entrypoint for maintenance tasks | `fast-validate` |
| tests/docker-compose.test.yml | Test harness | Spins up services for integration tests | Compose file |
| requirements.txt | Python dependencies | Defines runtime packages | package pins |
| composer.json | PHP library metadata | Declares PHP version and autoloading | package manifest |

## Dependencies

**Language & toolchain:** Python 3.11, PHP 8.2
**Packages (top-level):**

* Python: aiohttp, apscheduler, argon2-cffi, discord.py, python-dotenv, prometheus-client, SQLAlchemy, alembic, PyYAML, jsonschema, telethon
* Node: _none_
* Go: _none_
* Rust: _none_
**System deps / services:** PostgreSQL 15
**Where defined:** requirements.txt, composer.json, docker-compose.yml
**Install snippets:**

```bash
# Python
uv venv && source .venv/bin/activate && uv pip install -e .[dev]
# Node
npm ci
# Go
go build ./...
# Rust
cargo build
```

## Configuration & Secrets

**Config files:** `.env.example`, `config.yaml`
**Required env vars:**

| Key | Purpose | Default/Example |
| --- | ------- | --------------- |
| FETLIFE_USERNAME | FetLife account username | your_username |
| FETLIFE_PASSWORD | FetLife account password | your_password |
| CREDENTIAL_SALT | Pepper for credential hashing | example_salt |
| DISCORD_TOKEN | Discord bot token | your_token |
| TELEGRAM_API_ID | Telegram API ID | 123456 |
| TELEGRAM_API_HASH | Telegram API hash | your_api_hash |
| ADAPTER_AUTH_TOKEN | Shared adapter auth token | adapter_token |
| ADAPTER_BASE_URL | Adapter service URL (HTTPS) | https://adapter:8000 |
| DB_HOST | Database host | localhost |
| DB_PORT | Database port | 5432 |
| DB_NAME | Database name | fetlife_bot |
| DB_USER | Database user | bot_user |
| DB_PASSWORD | Database password | bot_password |
| DATABASE_URL | Full DB URL | postgresql://bot_user:bot_password@localhost:5432/fetlife_bot |
| FETLIFE_PROXY | Optional proxy URL | http://proxy:8080 |
| FETLIFE_PROXY_TYPE | Proxy type for libcurl | CURLPROXY_HTTP |
| FETLIFE_PROXY_USERNAME | Proxy basic auth user | proxy_user |
| FETLIFE_PROXY_PASSWORD | Proxy basic auth password | proxy_password |
| MGMT_PORT | Web UI port | 8000 |
| SESSION_SECRET | Session signing key | change_me |
| DISCORD_CLIENT_ID | OAuth client ID | your_client_id |
| DISCORD_CLIENT_SECRET | OAuth client secret | your_client_secret |
| OAUTH_REDIRECT_URI | OAuth callback URL | http://localhost:8000/oauth/callback |
| ADMIN_IDS | Comma-separated admin Discord IDs | 1234567890 |

```env
# .env.example
FETLIFE_USERNAME=your_username
DISCORD_TOKEN=__SET_ME__
ADAPTER_BASE_URL=https://adapter:8000
```

## How to Run

```bash
docker compose up -d
# or
python -m bot.main
```

**Health/Readiness (if any):** `http://localhost:8000/ready`
**Common tasks:** lint, build, test
* Deployment validation: `scripts/deploy-validate.sh`

## Testing & Quality

* How to run tests: `docker-compose -f tests/docker-compose.test.yml run --rm -e MOCK_ADAPTER=1 bot-test`
* Coverage or critical test targets: `bot/tests`
* Lint/type tools: `docker-compose run --rm bot sh -c "pip install -r requirements-dev.txt && black --check bot && flake8 bot && mypy bot"`

## Release & Versioning

* SemVer policy: BREAKING/! → MAJOR; feat → MINOR; fix/docs/ci/test/chore → PATCH
* CHANGELOG: `CHANGELOG.md`
* Release flow: PR → CI → tag → publish (no direct pushes to default)

## Ops Notes

* `scripts/install.sh` defaults to `--dry-run` and requires `--confirm` for changes.
* Docker/Compose images: `postgres:15`, local `bot` and `adapter` builds
* CI workflows: `.github/workflows/release-hygiene.yml`, `.github/workflows/release.yml`, `.github/workflows/deploy-validation.yml`
* Metrics/Logs/Tracing: Prometheus metrics at `/metrics`

## Workflow Examples

- **Audit logs:** `/audit search user:123 action:ban` → records stored via `bot/audit.py` and viewable at `/audit`.
- **Accounts:** add or remove FetLife logins at `/accounts`; credentials stored via `bot/storage.py`.
- **Timers:** `/timer 10m cleanup` → `apscheduler` schedules deletion in `bot/tasks.py`.
- **Birthdays:** `/birthday set 2000-01-01` → `bot/birthday.py` saves the date and daily jobs announce in configured channels.
- **Polls:** `/poll create "Best snack?" type:multiple options:"chips; cookies"` → `bot/polling.py` tracks votes and auto-closes.
- **Moderation:** `/mute @user 10m` → `bot/moderation.py` logs an infraction and `bot/audit.py` records the action.
- **Welcome:** `/welcome setup channel:#introductions message:"Welcome {user}" verify-role:@member` → `bot/welcome.py` sends messages and logs joins.

## Gaps & Assumptions

* No dedicated Node/Go components; install snippets left as placeholders.
* Adapter relies on FetLife's web interface; changes to site may break scraping.
