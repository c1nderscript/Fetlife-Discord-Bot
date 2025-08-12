import asyncio
import json
import os
import time
import logging
import random
import re
from datetime import datetime, timedelta
from typing import Any, Dict

import discord
import discord.abc
from aiohttp import web, ClientError
from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore[import-untyped]
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Summary,
    generate_latest,
)

from . import storage, adapter_client, models
from .config import get_channel_config, load_config, save_config
from .rate_limit import TokenBucket
from .telegram_bridge import TelegramBridge

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
ADAPTER_BASE_URL = os.getenv("ADAPTER_BASE_URL", "http://adapter:8080")
TELEGRAM_API_ID = int(os.getenv("TELEGRAM_API_ID", "0"))
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:  # pragma: no cover - formatting
        base = {
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        return json.dumps(base)


handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logging.basicConfig(level=logging.INFO, handlers=[handler])
logger = logging.getLogger("flbot")


# Metrics
messages_sent = Counter("discord_messages_sent_total", "Messages sent by bot")
fetlife_requests = Counter("fetlife_requests_total", "Requests made to FetLife")
poll_cycle = Summary("poll_cycle_seconds", "Duration of poll cycles")
duplicates_suppressed = Counter(
    "duplicates_suppressed_total", "Duplicate messages not relayed"
)
adapter_tokens = Gauge(
    "adapter_rate_limit_tokens", "Tokens currently available for adapter"
)
bot_tokens = Gauge("bot_rate_limit_tokens", "Tokens currently available for bot")

adapter_bucket = TokenBucket(5, 1)
bot_bucket = TokenBucket(5, 1)

fl_group = app_commands.Group(name="fl", description="FetLife commands")
account_group = app_commands.Group(
    name="account", description="Manage FetLife accounts", parent=fl_group
)
telegram_group = app_commands.Group(
    name="telegram", description="Manage Telegram relays", parent=fl_group
)


async def poll_adapter(db, sub_id: int, data: Dict[str, Any]):
    """Poll adapter with jitter and backoff, caching cursor and deduping."""
    start = time.perf_counter()
    await adapter_bucket.acquire()
    adapter_tokens.set(adapter_bucket.get_tokens())
    success = True
    try:
        sub = db.get(models.Subscription, sub_id)
        if not sub:
            raise RuntimeError("subscription missing")
        last_seen, last_ids = storage.get_cursor(db, sub_id)
        items: list[dict[str, Any]] = []
        if sub.type == "events":
            items = await adapter_client.fetch_events(
                ADAPTER_BASE_URL, sub.target_id, account_id=sub.account_id
            )
        elif sub.type == "writings":
            items = await adapter_client.fetch_writings(
                ADAPTER_BASE_URL, sub.target_id, account_id=sub.account_id
            )
        elif sub.type == "group_posts":
            items = await adapter_client.fetch_group_posts(
                ADAPTER_BASE_URL, sub.target_id, account_id=sub.account_id
            )
        elif sub.type == "attendees":
            items = await adapter_client.fetch_attendees(
                ADAPTER_BASE_URL, sub.target_id, account_id=sub.account_id
            )
        fetlife_requests.inc()
        channel = bot.get_channel(sub.channel_id)
        new_ids: list[str] = []
        for item in items:
            item_id = str(item.get("id"))
            if not item_id:
                continue
            if storage.has_relayed(db, sub_id, item_id):
                duplicates_suppressed.inc()
                logger.info("duplicate", extra={"sub_id": sub_id, "item": item_id})
                continue
            storage.record_relay(db, sub_id, item_id)
            if isinstance(channel, discord.abc.Messageable):
                if sub.type == "attendees":
                    embed = discord.Embed(
                        title=item.get("nickname", ""),
                        description=item.get("comment") or "",
                    )
                    if item.get("status"):
                        embed.add_field(name="Status", value=item["status"])
                else:
                    embed = discord.Embed(
                        title=item.get("title", ""), url=item.get("link")
                    )
                    if sub.type == "events" and item.get("time"):
                        embed.add_field(name="Start", value=item["time"])
                    if sub.type in ("writings", "group_posts") and item.get(
                        "published"
                    ):
                        embed.add_field(name="Published", value=item["published"])
                await bot_bucket.acquire()
                bot_tokens.set(bot_bucket.get_tokens())
                await channel.send(embed=embed)
                messages_sent.inc()
            new_ids.append(item_id)
        if new_ids:
            storage.update_cursor(db, sub_id, datetime.utcnow(), new_ids)
    except ClientError as exc:  # pragma: no cover - network error path
        logger.error("poll_http_error", extra={"sub_id": sub_id, "error": str(exc)})
        success = False
    except Exception as exc:  # pragma: no cover - error path
        logger.error("poll_error", extra={"sub_id": sub_id, "error": str(exc)})
        success = False
    finally:
        poll_cycle.observe(time.perf_counter() - start)
        adapter_tokens.set(adapter_bucket.get_tokens())
        bot.last_poll = time.time()

    interval = data.get("interval", 60)
    backoff = data.get("backoff", interval)
    if success:
        backoff = interval
    else:
        backoff = min(backoff * 2, interval * 60)
    jitter = random.uniform(0, interval * 0.1)
    run_in = backoff + jitter
    data["backoff"] = backoff
    bot.scheduler.add_job(
        poll_adapter,
        args=[db, sub_id, data],
        id=str(sub_id),
        replace_existing=True,
        run_date=datetime.utcnow() + timedelta(seconds=run_in),
    )


class FLBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        super().__init__(command_prefix="/", intents=intents)
        self.db = storage.init_db()
        self.scheduler = AsyncIOScheduler()
        self.config = load_config()
        self.bridge = TelegramBridge(
            self,
            api_id=TELEGRAM_API_ID if TELEGRAM_API_ID else None,
            api_hash=TELEGRAM_API_HASH,
            config=self.config,
        )
        self.last_poll = 0.0

    async def setup_hook(self) -> None:
        self.scheduler.start()


bot = FLBot()
ready_flag = False


@bot.event
async def on_ready() -> None:
    global ready_flag
    ready_flag = True
    logger.info("bot_ready", extra={"user": str(bot.user)})


@fl_group.command(name="login", description="Validate adapter service connectivity")
async def fl_login(interaction: discord.Interaction) -> None:
    try:
        ok = await adapter_client.login_adapter(ADAPTER_BASE_URL)
        msg = "Adapter login successful" if ok else "Adapter login failed"
    except ClientError as exc:  # pragma: no cover - network error path
        msg = f"Adapter login failed: {exc}"
    await bot_bucket.acquire()
    bot_tokens.set(bot_bucket.get_tokens())
    await interaction.response.send_message(msg)


@account_group.command(name="add", description="Add a FetLife account")
@app_commands.default_permissions(administrator=True)
async def fl_account_add(
    interaction: discord.Interaction, username: str, password: str
) -> None:
    try:
        if not getattr(
            getattr(interaction.user, "guild_permissions", None), "administrator", False
        ):
            raise PermissionError("Administrator permissions required")
        acct_id = storage.add_account(bot.db, username, password)
        await adapter_client.login(
            ADAPTER_BASE_URL, username, password, account_id=acct_id
        )
        await bot_bucket.acquire()
        bot_tokens.set(bot_bucket.get_tokens())
        await interaction.response.send_message(f"Account {acct_id} added")
    except Exception as exc:  # pragma: no cover - simple error path
        await bot_bucket.acquire()
        bot_tokens.set(bot_bucket.get_tokens())
        await interaction.response.send_message(str(exc), ephemeral=True)


@account_group.command(name="list", description="List stored accounts")
async def fl_account_list(interaction: discord.Interaction) -> None:
    accounts = storage.list_accounts(bot.db)
    if not accounts:
        await bot_bucket.acquire()
        bot_tokens.set(bot_bucket.get_tokens())
        await interaction.response.send_message("No accounts")
        return
    desc = "\n".join(f"`{aid}` {name}" for aid, name in accounts)
    embed = discord.Embed(title="Accounts", description=desc)
    await bot_bucket.acquire()
    bot_tokens.set(bot_bucket.get_tokens())
    await interaction.response.send_message(embed=embed)


@account_group.command(name="remove", description="Remove an account")
@app_commands.default_permissions(administrator=True)
async def fl_account_remove(interaction: discord.Interaction, account_id: int) -> None:
    try:
        if not getattr(
            getattr(interaction.user, "guild_permissions", None), "administrator", False
        ):
            raise PermissionError("Administrator permissions required")
        storage.remove_account(bot.db, account_id)
        await bot_bucket.acquire()
        bot_tokens.set(bot_bucket.get_tokens())
        await interaction.response.send_message(f"Removed account {account_id}")
    except Exception as exc:  # pragma: no cover - simple error path
        await bot_bucket.acquire()
        bot_tokens.set(bot_bucket.get_tokens())
        await interaction.response.send_message(str(exc), ephemeral=True)


@telegram_group.command(name="add", description="Relay a Telegram chat to a channel")
@app_commands.default_permissions(administrator=True)
async def fl_telegram_add(
    interaction: discord.Interaction, chat_id: str, channel: discord.TextChannel
) -> None:
    try:
        if not getattr(
            getattr(interaction.user, "guild_permissions", None), "administrator", False
        ):
            raise PermissionError("Administrator permissions required")
        bot.bridge.add_mapping(int(chat_id), channel.id)
        bot.config.setdefault("telegram_bridge", {}).setdefault("mappings", {})[
            str(chat_id)
        ] = str(channel.id)
        save_config(bot.config)
        await bot_bucket.acquire()
        bot_tokens.set(bot_bucket.get_tokens())
        await interaction.response.send_message("Added Telegram relay")
    except Exception as exc:  # pragma: no cover - simple error path
        await bot_bucket.acquire()
        bot_tokens.set(bot_bucket.get_tokens())
        await interaction.response.send_message(str(exc), ephemeral=True)


@telegram_group.command(name="remove", description="Stop relaying a Telegram chat")
@app_commands.default_permissions(administrator=True)
async def fl_telegram_remove(interaction: discord.Interaction, chat_id: str) -> None:
    try:
        if not getattr(
            getattr(interaction.user, "guild_permissions", None), "administrator", False
        ):
            raise PermissionError("Administrator permissions required")
        bot.bridge.remove_mapping(int(chat_id))
        bot.config.get("telegram_bridge", {}).get("mappings", {}).pop(
            str(chat_id), None
        )
        save_config(bot.config)
        await bot_bucket.acquire()
        bot_tokens.set(bot_bucket.get_tokens())
        await interaction.response.send_message("Removed Telegram relay")
    except Exception as exc:  # pragma: no cover - simple error path
        await bot_bucket.acquire()
        bot_tokens.set(bot_bucket.get_tokens())
        await interaction.response.send_message(str(exc), ephemeral=True)


@telegram_group.command(name="list", description="Show active Telegram relays")
async def fl_telegram_list(interaction: discord.Interaction) -> None:
    mappings = bot.bridge.mappings
    if mappings:
        desc = "\n".join(f"{cid} -> <#{chan}>" for cid, chan in mappings.items())
    else:
        desc = "No Telegram relays configured"
    embed = discord.Embed(title="Telegram Relays", description=desc)
    await bot_bucket.acquire()
    bot_tokens.set(bot_bucket.get_tokens())
    await interaction.response.send_message(embed=embed)


@fl_group.command(name="subscribe", description="Create a new subscription")
@app_commands.describe(
    sub_type="Type of content to subscribe to",
    target="Target identifier: user:<nickname> for writings, location:<...> for events, group:<id> for group posts, event:<id> for attendees",
    filters="Optional JSON filters",
    account="ID of stored account to use",
)
@app_commands.choices(
    sub_type=[
        app_commands.Choice(name="events", value="events"),
        app_commands.Choice(name="writings", value="writings"),
        app_commands.Choice(name="group_posts", value="group_posts"),
        app_commands.Choice(name="attendees", value="attendees"),
    ]
)
async def fl_subscribe(
    interaction: discord.Interaction,
    sub_type: str,
    target: str,
    filters: str | None = None,
    account: int | None = None,
) -> None:
    """Subscribe channel to FetLife events, writings, group posts, or attendees.

    target formats: `user:<nickname>` for writings, `location:<...>` for events,
    `group:<id>` for group posts, `event:<id>` for attendees.
    """
    if filters:
        try:
            filters_json = json.loads(filters)
        except json.JSONDecodeError:
            await bot_bucket.acquire()
            bot_tokens.set(bot_bucket.get_tokens())
            await interaction.response.send_message("Invalid JSON for filters")
            return
    else:
        filters_json = {}
    if sub_type == "group_posts" and not re.fullmatch(r"group:\d+", target):
        await bot_bucket.acquire()
        bot_tokens.set(bot_bucket.get_tokens())
        await interaction.response.send_message("Target must be group:<id>")
        return
    channel_id = interaction.channel_id
    if channel_id is None:
        await interaction.response.send_message("Channel not found")
        return
    sub_id = storage.add_subscription(
        bot.db,
        channel_id,
        sub_type,
        target,
        filters_json,
        account_id=account,
    )
    sub = bot.db.get(models.Subscription, sub_id)
    bot.scheduler.add_job(
        poll_adapter,
        args=[bot.db, sub_id, {"interval": 60, "type": sub.type if sub else sub_type}],
        id=str(sub_id),
    )
    await bot_bucket.acquire()
    bot_tokens.set(bot_bucket.get_tokens())
    await interaction.response.send_message(f"Subscribed with id {sub_id}")


@fl_group.command(name="list", description="List channel subscriptions")
async def fl_list(interaction: discord.Interaction) -> None:
    channel_id = interaction.channel_id
    if channel_id is None:
        await interaction.response.send_message("Channel not found")
        return
    subs = storage.list_subscriptions(bot.db, channel_id)
    if not subs:
        await bot_bucket.acquire()
        bot_tokens.set(bot_bucket.get_tokens())
        await interaction.response.send_message("No subscriptions")
        return
    desc = "\n".join(f"`{sid}` {typ} {tgt} (acct {aid})" for sid, typ, tgt, aid in subs)
    embed = discord.Embed(title="Subscriptions", description=desc)
    await bot_bucket.acquire()
    bot_tokens.set(bot_bucket.get_tokens())
    await interaction.response.send_message(embed=embed)


@fl_group.command(name="unsubscribe", description="Remove a subscription")
async def fl_unsubscribe(interaction: discord.Interaction, sub_id: int) -> None:
    channel_id = interaction.channel_id
    if channel_id is None:
        await interaction.response.send_message("Channel not found")
        return
    storage.remove_subscription(bot.db, sub_id, channel_id)
    try:
        bot.scheduler.remove_job(str(sub_id))
    except Exception:
        pass
    await bot_bucket.acquire()
    bot_tokens.set(bot_bucket.get_tokens())
    await interaction.response.send_message(f"Unsubscribed {sub_id}")


@fl_group.command(name="test", description="Preview an embed")
async def fl_test(interaction: discord.Interaction, sub_id: int) -> None:
    embed = discord.Embed(title="Test Notification", description=f"sub {sub_id}")
    await bot_bucket.acquire()
    bot_tokens.set(bot_bucket.get_tokens())
    await interaction.response.send_message(embed=embed)
    messages_sent.inc()
    channel_id = interaction.channel_id
    if channel_id is None:
        return
    db_settings = storage.get_channel_settings(bot.db, channel_id)
    cfg = get_channel_config(bot.config, interaction.guild_id, channel_id)
    settings = {**db_settings, **cfg}
    if settings.get("thread_per_event"):
        await bot_bucket.acquire()
        bot_tokens.set(bot_bucket.get_tokens())
        await interaction.followup.send("Thread created", ephemeral=True)


@fl_group.command(name="settings", description="Per-channel configuration")
async def fl_settings(
    interaction: discord.Interaction, key: str | None = None, value: str | None = None
) -> None:
    channel_id = interaction.channel_id
    if channel_id is None:
        await interaction.response.send_message("Channel not found")
        return
    if key and value:
        storage.set_channel_settings(bot.db, channel_id, **{key: value})
        await bot_bucket.acquire()
        bot_tokens.set(bot_bucket.get_tokens())
        await interaction.response.send_message("Updated settings")
    else:
        db_settings = storage.get_channel_settings(bot.db, channel_id)
        cfg = get_channel_config(bot.config, interaction.guild_id, channel_id)
        settings = {**db_settings, **cfg}
        await bot_bucket.acquire()
        bot_tokens.set(bot_bucket.get_tokens())
        await interaction.response.send_message(json.dumps(settings or {}))


@fl_group.command(name="health", description="Show adapter health")
async def fl_health(interaction: discord.Interaction) -> None:
    depth = len(bot.scheduler.get_jobs())
    last = (
        datetime.utcfromtimestamp(bot.last_poll).isoformat()
        if bot.last_poll
        else "never"
    )
    await bot_bucket.acquire()
    bot_tokens.set(bot_bucket.get_tokens())
    await interaction.response.send_message(f"last_poll: {last}; queue_depth: {depth}")


@fl_group.command(name="purge", description="Purge local caches")
@app_commands.default_permissions(administrator=True)
async def fl_purge(interaction: discord.Interaction) -> None:
    try:
        if not getattr(
            getattr(interaction.user, "guild_permissions", None), "administrator", False
        ):
            raise PermissionError("Administrator permissions required")
        await bot_bucket.acquire()
        bot_tokens.set(bot_bucket.get_tokens())
        await interaction.response.send_message("Purged")
    except Exception as exc:  # pragma: no cover - simple error path
        await bot_bucket.acquire()
        bot_tokens.set(bot_bucket.get_tokens())
        await interaction.response.send_message(str(exc), ephemeral=True)


async def metrics_handler(request: web.Request) -> web.Response:
    data = generate_latest()
    return web.Response(body=data, content_type=CONTENT_TYPE_LATEST)


async def ready_handler(request: web.Request) -> web.Response:
    if ready_flag:
        return web.Response(text="ok")
    return web.Response(status=503, text="not ready")


async def main() -> None:
    if not TOKEN:
        raise RuntimeError("DISCORD_TOKEN is not set")
    app = web.Application()
    app.router.add_get("/metrics", metrics_handler)
    app.router.add_get("/ready", ready_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8000)
    await site.start()
    await bot.bridge.start()
    try:
        await bot.start(TOKEN)
    finally:
        await bot.bridge.stop()
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
