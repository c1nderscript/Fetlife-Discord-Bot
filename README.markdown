# libFetLife - README

`libFetLife` is a PHP class implementing a simple API useful for interfacing with the amateur porn and fetish dating website [FetLife.com](https://fetlife.com/). Learn more [about the political motivation for this library](https://web.archive.org/web/20150912020717/https://bandanablog.wordpress.com/2015/04/30/fetlifes-best-customers/).

## Discord Bot

The `bot/` directory contains a Python application using `discord.py` that relays FetLife updates into Discord. It implements `/fl` slash commands for managing subscriptions, `/timer` for self-deleting messages, `/autodelete` for per-channel defaults, moderation commands like `/warn`, `/mute`, `/kick`, `/ban`, `/timeout`, `/modlog`, `/purge`, `/poll` for gathering yes/no, multiple choice, or ranked responses with automatic closing and web UI analytics, `/welcome setup` for configurable welcome messages and optional verification, and exposes Prometheus metrics at `/metrics` plus a readiness probe at `/ready`. Metrics include counters such as `fetlife_requests_total`, `discord_messages_sent_total`, `duplicates_suppressed_total`, `adapter_errors_total`, and `bot_errors_total`; histograms like `poll_cycle_seconds`, `adapter_request_latency_seconds`, and `bot_request_latency_seconds`; and gauges such as `rate_limit_tokens`, `internal_queue_depth`, and `telegram_bridge_connected`. Configuration is read from a `.env` file and an optional `config.yaml`.

### Logging and Tracing

Structured JSON logs are emitted to stdout. A correlation ID is generated for each operation and propagated via `contextvars`. All log entries include `correlation_id` in their `extra` fields to enable cross-service tracing.

### Resilience

Adapter requests use a circuit breaker. After repeated failures the breaker opens for a cooldown period, empty results are returned, and `adapter_circuit_breaker_state` reports the status via Prometheus.

### Docker Compose Quick Start

1. `bash scripts/install.sh` and select **Install**. This creates `.venv` and installs runtime and development dependencies.
2. `docker compose up -d` to launch the adapter, bot, and database. The `db` service pins
   `postgres:15` to digest `sha256:0de3e43bbb424d5fb7ca1889150f8e1b525d6c9fbaf9df6d853dcbc2ed5ffa1e` for reproducible builds.
3. Generate an invite link from the [Discord Developer Portal](https://discord.com/developers/applications), invite the bot to your server, then run `/fl login` to verify adapter authentication, `/fl subscribe events location:cities/5898 min_attendees:10`, `/fl subscribe group_posts group:1`, `/fl subscribe messages inbox`, `/fl list`, and `/fl test <id>` in Discord.

### Rolling Updates

`docker-compose.yml` configures `depends_on` with `condition: service_healthy` and a `deploy.update_config` of `order: start-first` to enable rolling updates. During deployments, new containers start and pass health checks before old ones stop, reducing downtime.

### Environment Variables

Copy `.env.example` to `.env` and fill in your values. The `.env` file supports these keys:

- `FETLIFE_USERNAME` – FetLife account username.
- `FETLIFE_PASSWORD` – FetLife account password.
- `CREDENTIAL_SALT` – optional string combined with credentials before hashing.
- `DISCORD_TOKEN` – Discord bot token.
- `TELEGRAM_API_ID`, `TELEGRAM_API_HASH` – optional Telegram API credentials for the bridge.
- `ADAPTER_AUTH_TOKEN` – shared token clients must send via `Authorization: Bearer` to the adapter.
- `ADAPTER_BASE_URL` – HTTPS base URL for the adapter service (default `https://adapter:8000`). Override via the `ADAPTER_BASE_URL` environment variable if the adapter is exposed elsewhere. This value must begin with `https://`; the bot exits otherwise. For local tests with the mock adapter you may set `MOCK_ADAPTER=1` to permit HTTP.
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` – database connection settings.
- `DATABASE_URL` – optional full connection URL that overrides the above.
- `FETLIFE_PROXY`, `FETLIFE_PROXY_TYPE`, `FETLIFE_PROXY_USERNAME`, `FETLIFE_PROXY_PASSWORD` – optional proxy configuration.
- `MGMT_PORT` – port for the management web interface (default `8000`).
- `SESSION_SECRET` – secret key for signing management UI sessions.
- `DISCORD_CLIENT_ID`, `DISCORD_CLIENT_SECRET`, `OAUTH_REDIRECT_URI` – Discord OAuth2 credentials for admin login.
- `ADMIN_IDS` – comma-separated Discord user IDs allowed to access the management UI.

### Health Checks and Deployment Validation

`scripts/health-check.sh` probes the bot and adapter readiness and metrics endpoints. It refuses to run as root and defaults to a dry run; pass `--confirm` to execute the `curl` checks. Retries and wait intervals are configurable via `HEALTH_RETRIES` (default `5`) and `HEALTH_INTERVAL` in seconds (default `2`). `make health` wraps this script with `--confirm`, forwards any environment overrides, and is used by CI to gate merges.

`scripts/deploy-validate.sh` verifies required secrets (`SESSION_SECRET`, `ADAPTER_AUTH_TOKEN`, `ADMIN_IDS`, `DATABASE_URL`, `ADAPTER_BASE_URL`), ensures `ADAPTER_BASE_URL` uses `https://`, confirms the adapter responds with `200` on `/healthz` and allows an authenticated `/login` request, retries failed checks with incremental backoff, confirms database connectivity, and ensures a TLS certificate exists at `TLS_CERT_PATH` (default `certs/tls.crt`). CI invokes this script to validate deployment environments.

Both scripts assume the database is ready and the adapter is served over HTTPS in production. Set `ADAPTER_BASE_URL` to an `https://` address and provide valid certificates for external deployments.

### Management Web Interface

After configuring the above variables, start the bot and visit `http://localhost:<MGMT_PORT>/`.
Log in with Discord; only IDs listed in `ADMIN_IDS` may access the interface. Each page mirrors a
slash command and requires the bot to hold the noted Discord permissions:

- **Subscriptions** – `/subscriptions`
  - Manage channel subscriptions.
  - Permission: none beyond login.
  - Example:

    ```text
    ID  Type      Target
    1   events    location:12345
    ```

- **Reaction Roles** – `/roles`
  - Map message reactions to roles.
  - Requires **Manage Roles**.
  - Example removal form:

    ```text
    Message ID: 123 | Emoji: 👍 | Role ID: 456
    ```

- **Channels** – `/channels`
  - Edit per-channel settings such as thread options.
  - Requires **Manage Channels**.
  - Example settings payload:

    ```json
    {"autodelete": 3600}
    ```

- **Birthdays** – `/birthdays`
  - View stored birthdays.

- **Polls** – `/polls`
  - Create, close, and view polls.
  - Example:

    ```text
    Question: Best snack?
    Type: multiple
    Options: chips;cookies
    ```

- **Timed Messages** – `/timers` (`/timed-messages`)
  - Schedule self-deleting messages.

- **Auto-Delete Defaults** – `/autodelete`
  - Set default deletion timers.
  - Requires **Administrator**.

- **Welcome Configuration** – `/welcome`
  - Configure welcome message and optional verification role.
  - Requires **Administrator**.
  - Example template:

    ```text
    Welcome {user} to the server!
    ```

- **Moderation Tools** – `/moderation`
  - Forms for warn, mute, kick, ban, timeout, and purge.
  - Requires relevant moderation permissions (Kick Members, Ban Members, Manage Messages).

- **Appeals Dashboard** – `/appeals`
  - Review and resolve member appeals.
  - Requires **Administrator**.

- **Audit Logs** – `/audit`
  - View recorded management actions.

Pages render using Jinja2 templates stored under `bot/templates/`.

### Audit Logs

Use `/audit search user:123 action:ban` to list ban actions taken by user `123`.
The management UI at `/audit` exposes the same records with filtering and pagination.

### Timed Messages

Send self-deleting messages with `/timer <duration> <content>`.
Example: `/timer 10m Remember to stretch` deletes the reminder after ten minutes.
Set channel defaults with `/autodelete enable 1h` and disable with `/autodelete disable`.
Existing timers can be reviewed or scheduled through the management UI at `/timers`. Channel
defaults may be configured at `/autodelete`.

### Poll Commands

Use `/poll create` to open a poll. Specify `yes/no`, `multiple`, or `ranked` types and provide
semicolon-separated options for multi-option polls. Polls may auto-close after a duration.
Example: `/poll create "Best snack?" type:multiple options:"chips;cookies"`.
`/poll list` shows active polls, `/poll close` ends a poll early, and `/poll results` displays vote
counts. Poll statistics and manual poll creation are available in the management UI at `/polls`.

### Birthday Reminders

Configure a `birthday_channel` for each guild in `config.yaml` to receive daily birthday announcements.
Members can manage entries with `/birthday set 2000-01-01`, `/birthday list`, and `/birthday remove`.
The command supports time zones, a privacy flag to hide mentions, and an optional role assignment
applied on the user's birthday. A calendar view is available in the management UI at `/birthdays`.

### Moderation Commands

Server moderation tools include `/warn`, `/mute`, `/kick`, `/ban`, `/timeout`, `/modlog`, and `/purge`.
Examples:
`/warn @user Be respectful`, `/mute @user 10m`, and `/modlog` to review recent actions.

### Welcome Messages

Run `/welcome setup` to choose a channel, message template, and optional verification role for new members.
Use `{user}` in the message to mention the joining member and enable the `preview` option to send a sample.
If a verification role is configured, the bot sends a button that grants the role when clicked. Joins and
leaves are logged for auditing. Existing settings can also be managed from the web UI at `/welcome`, which
includes a preview option for the message template.

### Database Migrations

The schema is managed with Alembic. Apply migrations with:

```bash
alembic upgrade head
```

When using Docker Compose:

```bash
docker compose run --rm bot alembic upgrade head
```

### Cache Behavior

Events, profiles, and RSVP statuses are cached in the database. During polling, the bot
upserts these records before relaying messages to Discord, enabling deduplication and
future features. Use `/fl purge` to clear cached data when needed.

### Health Checks

Docker Compose declares health checks for both services using these endpoints. After the stack is running, `scripts/health-check.sh --confirm` or `make health` runs them manually.

- Adapter: `GET http://localhost:8000/healthz` for liveness and `GET http://localhost:8000/metrics` for Prometheus metrics.
- Bot: `GET http://localhost:8000/ready` for readiness and `GET http://localhost:8000/metrics` for Prometheus metrics.

### Manual Setup

1. `bash scripts/install.sh` and select **Install** to create `.venv` and install dependencies from `requirements.txt` and `requirements-dev.txt`. The `.env` file contains secrets and **must not** be committed to version control.
2. Customize `config.yaml` for per-guild or per-channel defaults. A minimal example:

   ```yaml
   defaults:
    thread_per_event: false
    admin_command_rate: 5
    admin_command_per: 60
   guilds:
     "123456789012345678":
       thread_per_event: true
       admin_command_rate: 10
       admin_command_per: 60
       channels:
         "234567890123456789":
           attendee_sample: 5
   telegram_bridge:
     mappings:
       "-1001234567890": "234567890123456789"
    ```

   This file is loaded at runtime; avoid storing credentials in it.
   Manage Telegram relays at runtime with `/fl telegram add`, `/fl telegram remove`, and `/fl telegram list`.

   Administrative commands like `/role`, `/channel`, and `/reactionrole` are rate limited. Defaults allow `5` uses per `60`
   seconds per guild and can be overridden with `admin_command_rate` and `admin_command_per` in `config.yaml`.

   The Telegram bridge automatically reconnects and forwards photos and documents as Discord attachments. For `messages` subscriptions, relayed DMs are also sent to the mapped Telegram chat.

### Channel Management

Use `/channel create <name>` to create text channels, `/channel delete <channel>` to remove them, and `/channel rename <channel> <name>` to rename an existing channel. These commands require the **Manage Channels** permission.

### Role Management

Use `/role add <user> <role_id>` to assign roles, `/role remove <user> <role_id>` to revoke them, and `/role list` to display available roles. These commands require the **Manage Roles** permission.

### Reaction Roles

Map reactions on a specific message to roles with `/reactionrole add <message_id> <emoji> <role_id>` and remove them with `/reactionrole remove <message_id> <emoji>`. When users add the configured reaction they receive the role; removing the reaction revokes it. These commands require the **Manage Roles** permission.

Run the bot with:

```bash
python -m bot.main
```

### Deployment

Validate environment readiness with [`scripts/deploy-validate.sh`](scripts/deploy-validate.sh), which now checks adapter HTTPS endpoints with retries and an authenticated login request.

For unattended deployments run [`scripts/setup.sh`](scripts/setup.sh) once to generate the `.env`, apply migrations, and perform initial configuration. Then choose one of the following options to keep the bot running continuously. The script prompts for `ADAPTER_AUTH_TOKEN`, `ADAPTER_BASE_URL`, `TELEGRAM_API_ID`, and `TELEGRAM_API_HASH`, using existing `.env` values as defaults.

#### Docker Compose

Ensure `restart: unless-stopped` is set in `docker-compose.yml` and launch the stack in the background:

```bash
docker compose up -d
```

Docker stores logs per container; view them with:

```bash
docker compose logs -f bot
```

#### systemd service

Create `/etc/systemd/system/fetlife-bot.service`:

```ini
[Unit]
Description=FetLife Discord Bot
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/fetlife-discord-bot
ExecStart=/usr/bin/python -m bot.main
Restart=on-failure
EnvironmentFile=/opt/fetlife-discord-bot/.env
StandardOutput=append:/var/log/fetlife-bot.log
StandardError=append:/var/log/fetlife-bot.log

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl enable --now fetlife-bot.service
```

View status and logs:

```bash
systemctl status fetlife-bot.service
journalctl -u fetlife-bot.service -f
```

## System requirements

To run `libFetLife`, you need PHP version 5.3.6 or greater (with [PHP's cURL extension](https://php.net/manual/book.curl.php) installed).

## Getting started

To use `libFetLife`, include it in your project and instantiate a new `FetLifeUser` object:

```php
// Load FetLife API.
require_once 'libFetLife/FetLife.php';

// Make a FetLifeUser (like a database handle).
$FL = new FetLifeUser('username', 'password');
```

You can optionally instruct `libFetLife` to use a proxy instead of making direction connections to FetLife.com:

```php
$FL->connection->setProxy('example.proxy.com:9050', CURLPROXY_SOCKS5); // Optional.
$FL->connection->setProxy('auto'); // or, set a new randomized proxy automatically.
```

When you're ready, login with the `FetLifeUser::logIn()` method:

```php
$FL->logIn();
```

Now `$FL` represents you on FetLife:

```php
// Print some basic information about the account you're using.
print $FL->id;       // your user's numeric ID.
print $FL->nickname; // your user's nickname, the name you signed in with
//etc.
```

You use the `FetLifeUser` object's various public methods to send queries to FetLife. Replies depend on the query method:

```php
// Query FetLife for information about other users.
print $FL->getUserIdByNickname('JohnBaku'); // prints "1"
print $FL->getUserNicknameById(1254);       // prints "maymay"
```

Other FetLife users are represented as FetLifeProfile objects:

```php
// Object-oriented access to user info is available as FetLifeProfile objects.
$profile = $FL->getUserProfile(1);          // Profile with ID 1
$profile->nickname;                         // "JohnBaku"
$profile->age;
$profile->gender;
$profile->role;

// the `adr` member is an array keyed like its eponymous microformat:
$profile->adr['locality'];     // "Vancouver"
$profile->adr['region'];       // "British Columbia"
$profile->adr['country-name']; // "Canada"

// Some FetLifeProfile methods:
$profile->getAvatarURL();     // optional $size parameter retrieves larger images
$profile->isPayingAccount();  // true if the profile has a "supporter" badge
$profile->getEvents();        // array of FetLifeEvent objects listed on the profile
$profile->getEventsGoingTo(); // array of FetLifeEvent the user has RSVP'ed "going" to
$profile->getGroups();        // array of FetLifeGroup objects listed on the profile
$profile->getGroupsLead();    // array of FetLifeGroups the user moderates
```

Many methods return arrays of `FetLifeProfile` objects. Since queries are live, they can also be passed an optional page limiter.

```php
// Get a user's friends list as an array of FetLifeProfile objects.
$friends = $FL->getFriendsOf('maymay');
// A numeric FetLife user ID also works.
$friends = $FL->getFriendsOf(1254);
// If there are many pages, you can set a limit.
$friends_partial = $FL->getFriendsOf('maymay', 3); // Only first 3 pages.

// Numerous other functions also return arrays, with optional page limit.
$members = $FL->getMembersOfGroup(11708); // "Kink On Tap"
$kinksters = $FL->getKinkstersWithFetish(193); // "Corsets"
$local_kinksters = $FL->getKinkstersInLocation('cities/5898'); // all kinksters in Balitmore, MD.
$attendees = $FL->getKinkstersGoingToEvent(149379);
$maybes = $FL->getKinkstersMaybeGoingToEvent(149379, 2); // Only 2 pages.
```

Most data objects, including `FetLifeProfile`, `FetLifeWriting`, and `FetLifePicture` are descended from a common `FetLifeContent` base class. Such descendants  have a `populate()` method that fetches supplemental information about the object from FetLife:

```php
// You can also fetch arrays of a user's FetLife data as objects this way.
$writings = $FL->getWritingsOf('JohnBaku'); // All of JohnBaku's Writings.
$pictures = $FL->getPicturesOf(1);          // All of JohnBaku's Pictures.

// If you want to fetch comments, you need to populate() the objects.
$writings_and_pictures = array_merge($writings, $pictures);
foreach ($writings_and_pictures as $item) {
    $item->comments;   // currently, returns an NULL
    $item->populate();
    $item->comments;   // now, returns an array of FetLifeComment objects.
}
```

FetLife events can be queried much like profiles:

```php
// If you already know the event ID, you can just fetch that event.
$event = $FL->getEventById(151424);
// "Populate" behavior works the same way.
$event = $FL->getEventById(151424, true); // Get all availble event data.

// You can also fetch arrays of events as FetLifeEvent objects.
$events = $FL->getUpcomingEventsInLocation('cities/5898'); // Get all events in Balitmore, MD.
// Or get just the first couple pages.
$events_partial = $FL->getUpcomingEventsInLocation('cities/5898', 2); // Only 2 pages.

// FetLifeEvent objects are instantiated from minimal data.
// To fill them out, call their populate() method.
$events[0]->populate(); // Flesh out data from first event fetched.
// RSVP lists take a while to fetch, but you can get them, too.
$events[1]->populate(2); // Fetch first 2 pages of RSVP responses.
$events[2]->populate(true); // Or fetch all pages of RSVP responses.

// Now we have access to some basic event data.
print $events[2]->getPermalink();
print $events[2]->venue_name;
print $events[2]->dress_code;
// etc...

// Attendee lists are arrays of FetLifeProfile objects, same as friends lists.
// You can collect a list of all participants
$everyone = $events[2]->getParticipants();

// or interact with the separate RSVP lists individually
foreach ($events[2]->going as $profile) {
    print $profile->nickname; // FetLife names of people who RSVP'd "Going."
}
$i = 0;
$y = 0;
foreach ($events[2]->maybegoing as $profile) {
    if ('Switch' === $profile->role) { $i++; }
    if ('M' === $profile->gender) { $y++; }
}
print "There are $i Switches and $y male-identified people maybe going to {$events[2]->title}.";
```

You can also perform basic searches:

```php
$kinksters = $FL->searchKinksters('maymay'); // All Kinksters whose username contains the query.
$partial_kinksters = $FL->searchKinksters('maymay', 5) // only first 5 pages of above results.
```

[Patches welcome](https://github.com/fabacab/libFetLife/issues/new). :)

## Testing

`libFetLife` uses [PHPUnit](https://phpunit.de/) for unit testing. The `tests/` directory includes a `phpunit.xml.sample` file with a default configuration. To run live tests, you need to edit this file so that the global variables `fetlife_username`, `fetlife_password,` and `fetlife_proxyurl` have the values you want to use to create the test runner's `FetLifeUser` object, as described above, and then copy it to `phpunit.xml`.

    cd libFetLife/tests               # Inside the tests directory...
    vi phpunit.xml.sample             # is a sample PHPUnit configuration file. Edit it.
    cp phpunit.xml.sample phpunit.xml # Then copy it to PHPUnit's expected location.

## Projects that use libFetLife

* [FetLife WordPress eXtended RSS Generator](https://github.com/fabacab/fetlife2wxr)
* [FetLife iCalendar](https://github.com/fabacab/fetlife-icalendar/)
* [FetLife Maltego](https://github.com/fabacab/fetlife-maltego/)
* [FetLife Export](https://github.com/fabacab/fetlife-export/)
* [FetLife Bridge](https://github.com/fabacab/fetlife-bridge/)

Are you using `libFetLife`? [Let me know](http://maybemaimed.com/seminars/#booking-inquiry).

## Adapter HTTP Service

The `adapter/` directory provides a small Slim-based HTTP service that wraps `FetLife.php`.
It reads credentials from environment variables (`FETLIFE_USERNAME`, `FETLIFE_PASSWORD`, `FETLIFE_PROXY`, `FETLIFE_PROXY_TYPE`) and exposes a `/healthz` endpoint along with Prometheus metrics at `/metrics`.
All requests must include an `Authorization: Bearer` token matching `ADAPTER_AUTH_TOKEN`.

### OpenAPI
The adapter's HTTP API is documented in
[adapter/openapi.yaml](adapter/openapi.yaml), served at
`/openapi.yaml` when the service is running.

### HTTPS Reverse Proxy

The adapter only serves HTTP on port `8000`. For public access, place it
behind a TLS-terminating reverse proxy such as Caddy or Nginx. Forward the
`Host`, `X-Forwarded-For`, and `X-Forwarded-Proto` headers so the service can
generate correct URLs and logs. The bot should then set
`ADAPTER_BASE_URL` to the external HTTPS address, for example:

```
ADAPTER_BASE_URL=https://adapter.example.com
```

**Caddy**

```Caddyfile
adapter.example.com {
    reverse_proxy 127.0.0.1:8000
}
```

**Nginx**

```nginx
server {
    listen 443 ssl;
    server_name adapter.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Contributing

Pull requests are welcome. Please:

- Limit each PR to a single feature or fix.
- Include tests and documentation updates.
- Run `make check` (lint, tests, schema) before submitting.
- Follow semantic commit messages and Conventional Changelog guidelines.
- Review [.codex-policy.yml](.codex-policy.yml) for branch protections, Conventional Commit requirements, required reviews, and security expectations.

## License

This project is licensed under the [GNU Affero General Public License v3.0 or later](LICENSE).

