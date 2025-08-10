This document is the development spec for a Discord bot that authenticates to FetLife via a fork of libFetLife and relays updates (events, attendees, writings/posts, group posts) into Discord channels with configurable filters.

1) Goals & Non-Goals
Goals
Authenticate to FetLife using libFetLife.

Poll and relay:

Events (title, time, venue, city/region, link)

RSVP lists (Going/Maybe/Not Going) + counts; optional attendee samples

User writings/posts with excerpt + link

Group posts (title + link)

Discord UX:

Slash commands to subscribe/unsubscribe sources (users, groups, locations, events).

Per-channel filters (location radius, keywords, content types, frequency).

Rich embeds, optional attendee sampling, thread-per-event option.

Reliability:

Idempotent relays (no dupes), caching, rate limiting, and backoff.

Observability (metrics, logs) and admin controls.

Non-Goals
Moderation features beyond basic filtering.

Full text/media mirroring (respect privacy; post excerpts + links only).

Public scraping beyond authenticated areas allowed by the account used.

2) High-Level Architecture
css
Copy
Edit
[Discord] <-> [Bot (Python or Node)] <-> [FetLife Adapter Service (PHP: libFetLife)]
                                   \-> [Cache/DB]  \-> [Queue/Scheduler]
                                   \-> [Metrics/Logs]
Discord Bot: Handles commands, subscriptions, formatting, and dispatch.

FetLife Adapter: Thin PHP service wrapping libFetLife (CLI or HTTP). Encapsulates login, pagination, and standardized JSON responses.

Storage: SQLite/Postgres (prod) for subscriptions, seen items, cursors, and audit logs.

Scheduler: Polls subscriptions; enqueues fetch tasks; processes results.

Config: .env + config.yaml per-guild/per-channel overrides.

Observability: Prometheus-style metrics endpoint + structured logs.

3) Data Model (minimal)
Tables
guilds(id, name, created_at)

channels(id, guild_id, name, created_at)

subscriptions(id, channel_id, type, target_id, target_kind, filters_json, created_by, created_at, active)

type: events|writings|group_posts|attendees

target_kind: user|group|location|event

filters_json: { keywords:[], city:"", region:"", radius_km: N, min_attendees: N, … }

cursors(subscription_id, last_seen_at, last_item_ids_json, updated_at)

relay_log(id, subscription_id, item_id, item_hash, relayed_at)

profiles(id, nickname, fl_id, last_seen_at) (optional cache)

events(id, fl_id, title, city, region, start_at, permalink, last_populated_at) (cache)

rsvps(event_id, profile_fl_id, status, seen_at) (optional cache)

4) Security, Privacy & Compliance
Credentials: Store FETLIFE_USERNAME, FETLIFE_PASSWORD, and DISCORD_TOKEN in .env/secrets manager. Never commit.

Auth Model: Use a dedicated FetLife account with explicit consent; keep session/cookies isolated.

ToS/Robots: Respect FetLife ToS. Implement conservative polling intervals and user-agent identification.

Data Minimization: Post excerpts and links; avoid relaying sensitive profile details; allow opt-out filters per channel.

GDPR/UK: Treat relayed content as transient notification; provide deletion controls (purge caches, forget channel data).

Rate Limiting: Token bucket at the adapter + bot layers. Exponential backoff on 4xx/5xx.

5) Discord Commands (Slash)
/fl login — (Admin only) Validate adapter service connectivity.
/fl subscribe <type> <target> [filters...]

type: events|writings|group_posts|attendees

target: user:<nickname> | group:<id|slug> | location:<city|region|cities/ID> | event:<id>

Filters (optional): keywords:, city:, region:, radius_km:, min_attendees:, since:
Examples:

/fl subscribe events location:cities/5898 radius_km:50 min_attendees:10

/fl subscribe attendees event:151424

/fl subscribe writings user:maymay keywords:"consent,ropes"

/fl unsubscribe <subscription_id>
/fl list — List channel subscriptions and status.
/fl test <subscription_id> — Dry run and preview an embed.
/fl settings [key value]... — Per-channel config (e.g., thread_per_event:on, attendee_sample:10).
/fl health — Show adapter health, queue depth, and last poll times.
/fl purge [scope] — Purge local caches for this channel or specific subscription.

6) Message Formatting (Embeds)
Event
Title: 📅 {event.title}

Fields:

Time: {start_at} ({tz})

Where: {venue_name or city, region}

RSVP: Going {n} | Maybe {m} (+ optional sample: nickname1, nickname2…)

Footer: FetLife • {permalink}

Writing/Post
Title: 📝 {post.title}

Description: first 300 chars w/ ellipsis

Author: {nickname}

Footer: FetLife • {permalink}

Group Post
Title: 💬 [{group.name}] {post.title}

Description: excerpt

Footer: link

7) Polling & Idempotency
Interval: Default 5–15 min per subscription type; jitter 10–25% to avoid thundering herd.

Cursors: Track last_seen_at and last_item_ids per subscription.

Dedupe: Hash on (type, target, item_id, key fields); check relay_log before posting.

Pagination: Adapter returns items[], next_cursor; loop until exhausted or safety limit.

Pseudo-flow:

text
Copy
Edit
for each active subscription:
  cursor = load_cursor()
  items = adapter.fetch(type, target, cursor)
  for item in items:
    if not seen(item): relay_to_discord(format(item)); log(item)
  save_cursor(items.last_cursor)
8) Adapter Service (PHP: libFetLife)
Two integration options; choose one:

A) HTTP Microservice (Recommended)
Endpoints (JSON):

POST /login -> session cookie cache

GET /events/upcoming?location=...&pages=...

GET /events/{id}?populate=true

GET /events/{id}/attendees?pages=...

GET /users/{nickname}/writings?pages=...

GET /groups/{id}/posts?pages=...

Config: proxy support (auto/SOCKS5), user-agent, timeouts, per-endpoint rate limits.

B) CLI Wrapper
Commands like:

php adapter.php events:upcoming --location=cities/5898 --pages=2

php adapter.php event:get --id=151424 --populate

php adapter.php user:writings --nickname=maymay --pages=3

Returns JSON to stdout.

Both should normalize output (UTC timestamps, stable IDs, minimal PII, direct permalink).

9) Configuration
.env

makefile
Copy
Edit
DISCORD_TOKEN=...
FETLIFE_USERNAME=...
FETLIFE_PASSWORD=...
ADAPTER_URL=http://fetlife-adapter:8080
DB_URL=postgresql://bot:bot@db/bot
HTTP_PROXY= # optional
config.yaml

yaml
Copy
Edit
defaults:
  poll:
    events_minutes: 10
    writings_minutes: 15
    group_posts_minutes: 15
    attendees_minutes: 30
  formatting:
    attendee_sample: 5
    thread_per_event: false
  filtering:
    blocked_keywords: []
    min_attendees: 0

guild_overrides:
  "123456789012345678": # Guild ID
    channels:
      "987654321098765432": # Channel ID
        formatting:
          thread_per_event: true
        filtering:
          keywords: ["rope", "class"]
          region: "Northern Ireland"
10) Deployment
Docker Compose (example stack):

discord-bot (Node.js or Python)

fetlife-adapter (PHP + libFetLife + cURL)

db (Postgres)

redis (optional: queues, rate limiter)

prometheus + grafana (optional)

Secrets via .env or Docker secrets.

Healthchecks: /healthz on adapter; bot exposes /metrics & /ready.

11) Testing
Unit: Command parsing, formatting, filter logic, dedupe.

Contract: JSON schema tests for adapter responses.

Integration: Docker Compose harness with mock adapter fixtures to simulate `/fl subscribe` and verify metrics; simulate pagination and errors.

Live: Opt-in; dedicated staging guild + test FetLife account; reduced scopes.

12) Observability & Ops
Metrics:

fetlife_requests_total{endpoint,status}

poll_cycle_seconds{type}

discord_messages_sent_total{type}

duplicates_suppressed_total

adapter_errors_total

Structured logs (JSON): include subscription_id, guild_id, channel_id, target.

Admin:

/fl health (exposes last poll, queue sizes, adapter status)

/fl purge (clear caches by scope)

Feature flags via config.yaml.

13) Error Handling & Backoff
4xx/5xx from adapter:

Retry with exponential backoff; circuit-break after N failures.

Post a one-time channel notice if subscription is paused due to errors.

Login failures:

Immediate alert in admin log channel; auto-retry with backoff.

Content parsing change:

Raise adapter_schema_mismatch warning; fallback to minimal link relay.

14) Roadmap
MVP

Adapter endpoints for: login, upcoming events (by location), event details + attendees, user writings.

Bot: subscribe/list/unsubscribe/test/health; event + writing relays; dedupe + cursors.

Next

Group post relays; thread-per-event; attendee samples.

Per-channel keyword & location filters.

Postgres migration & Prometheus metrics.

Later

Web dashboard for subscriptions.

Webhooks (if/ever supported) to reduce polling.

Multi-account adapter support, per-subscription credentials.

15) Quick Start (Dev)
bash
Copy
Edit
# 1) Launch adapter + bot (docker compose)
cp .env.example .env && edit .env
docker compose up -d

# 2) In Discord: invite the bot; run:
# /fl login   (admin channel)
# /fl subscribe events location:cities/5898 min_attendees:10
# /fl list
# /fl test <id-returned>
16) Notes on libFetLife
Ensure PHP ≥ 5.3.6 with cURL (modern PHP works; update deprecations if needed).

Prefer adapter normalization over exposing raw libFetLife objects.

Implement populate() pathways sparingly (attendees are expensive—paginate and cap).

17) Contribution Rules
One feature per PR; include tests and docs updates.

No secrets in code or logs.

Run make check (lint, tests, schema) before PR.

Follow semantic commits and Conventional Changelog.

18) Risk Register (tl;dr)
ToS/Access: Authentication may break if site changes → adapter abstraction + schema tests.

Rate/Blocks: Aggressive polling risks account blocks → jitter, backoff, low default rates.

Privacy: Relaying PII → excerpts + links; opt-out filters; cache purges.

Schema Drift: Site HTML changes → contract tests + fast adapter patch process.

Contact: Open an issue with logs (redacted), guild/channel IDs, subscription config, and adapter version.









19) CI & Release
release-hygiene GitHub workflow runs `make check`, ensures version in `pyproject.toml` matches `CHANGELOG.md`, and executes `scripts/agents-verify.sh`.
Releases are tagged from `main` and publish notes from `.github/RELEASE_NOTES.md`.
