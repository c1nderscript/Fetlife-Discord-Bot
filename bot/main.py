import asyncio
import json
import os
import time
import logging
from datetime import datetime
from typing import Any, Dict

import discord
from aiohttp import web
from apscheduler.schedulers.asyncio import AsyncIOScheduler
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

from . import storage
from .config import get_channel_config, load_config

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")


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
rate_limit_tokens = Gauge(
    "rate_limit_tokens", "Tokens currently available in rate limiter"
)

rate_limiter = asyncio.Semaphore(5)

fl_group = app_commands.Group(name="fl", description="FetLife commands")




async def poll_adapter(db, sub_id: int, data: Dict[str, Any]):
    """Placeholder polling job that would contact adapter service."""
    start = time.perf_counter()
    await rate_limiter.acquire()
    rate_limit_tokens.set(rate_limiter._value)
    try:
        item_id = "sample"
        fetlife_requests.inc()
        if storage.has_relayed(db, sub_id, item_id):
            duplicates_suppressed.inc()
            logger.info("duplicate", extra={"sub_id": sub_id, "item": item_id})
            return
        storage.record_relay(db, sub_id, item_id)
        await asyncio.sleep(0)
    finally:
        poll_cycle.observe(time.perf_counter() - start)
        rate_limiter.release()
        rate_limit_tokens.set(rate_limiter._value)
        bot.last_poll = time.time()


class FLBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        super().__init__(command_prefix="/", intents=intents)
        self.db = storage.init_db()
        self.scheduler = AsyncIOScheduler()
        self.config = load_config()
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
    await interaction.response.send_message("Adapter login successful")


@fl_group.command(name="subscribe", description="Create a new subscription")
async def fl_subscribe(
    interaction: discord.Interaction,
    sub_type: str,
    target: str,
    filters: str | None = None,
) -> None:
    filters_json = json.loads(filters) if filters else {}
    sub_id = storage.add_subscription(
        bot.db, interaction.channel_id, sub_type, target, filters_json
    )
    bot.scheduler.add_job(poll_adapter, args=[bot.db, sub_id, filters_json], id=str(sub_id))
    await interaction.response.send_message(f"Subscribed with id {sub_id}")


@fl_group.command(name="list", description="List channel subscriptions")
async def fl_list(interaction: discord.Interaction) -> None:
    subs = storage.list_subscriptions(bot.db, interaction.channel_id)
    if not subs:
        await interaction.response.send_message("No subscriptions")
        return
    desc = "\n".join(f"`{sid}` {typ} {tgt}" for sid, typ, tgt in subs)
    embed = discord.Embed(title="Subscriptions", description=desc)
    await interaction.response.send_message(embed=embed)


@fl_group.command(name="unsubscribe", description="Remove a subscription")
async def fl_unsubscribe(interaction: discord.Interaction, sub_id: int) -> None:
    storage.remove_subscription(bot.db, sub_id, interaction.channel_id)
    try:
        bot.scheduler.remove_job(str(sub_id))
    except Exception:
        pass
    await interaction.response.send_message(f"Unsubscribed {sub_id}")


@fl_group.command(name="test", description="Preview an embed")
async def fl_test(interaction: discord.Interaction, sub_id: int) -> None:
    embed = discord.Embed(title="Test Notification", description=f"sub {sub_id}")
    msg = await interaction.response.send_message(embed=embed)
    messages_sent.inc()
    db_settings = storage.get_channel_settings(bot.db, interaction.channel_id)
    cfg = get_channel_config(bot.config, interaction.guild_id, interaction.channel_id)
    settings = {**db_settings, **cfg}
    if settings.get("thread_per_event"):
        await interaction.followup.send("Thread created", ephemeral=True)


@fl_group.command(name="settings", description="Per-channel configuration")
async def fl_settings(
    interaction: discord.Interaction, key: str | None = None, value: str | None = None
) -> None:
    if key and value:
        storage.set_channel_settings(bot.db, interaction.channel_id, **{key: value})
        await interaction.response.send_message("Updated settings")
    else:
        db_settings = storage.get_channel_settings(bot.db, interaction.channel_id)
        cfg = get_channel_config(bot.config, interaction.guild_id, interaction.channel_id)
        settings = {**db_settings, **cfg}
        await interaction.response.send_message(json.dumps(settings or {}))


@fl_group.command(name="health", description="Show adapter health")
async def fl_health(interaction: discord.Interaction) -> None:
    depth = len(bot.scheduler.get_jobs())
    last = (
        datetime.utcfromtimestamp(bot.last_poll).isoformat()
        if bot.last_poll
        else "never"
    )
    await interaction.response.send_message(
        f"last_poll: {last}; queue_depth: {depth}"
    )


@fl_group.command(name="purge", description="Purge local caches")
async def fl_purge(interaction: discord.Interaction) -> None:
    await interaction.response.send_message("Purged")


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
    await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
