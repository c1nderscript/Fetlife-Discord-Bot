import asyncio
import json
import os
from typing import Any, Dict

import discord
from aiohttp import web
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest

from . import storage

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Metrics
messages_sent = Counter("discord_messages_sent_total", "Messages sent by bot")


async def poll_adapter(db, sub_id: int, data: Dict[str, Any]):
    """Placeholder polling job that would contact adapter service."""
    item_id = "sample"
    if storage.has_relayed(db, sub_id, item_id):
        return
    storage.record_relay(db, sub_id, item_id)
    await asyncio.sleep(0)


class FLBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        super().__init__(command_prefix="/", intents=intents)
        self.tree.add_command(fl_group)
        self.db = storage.init_db()
        self.scheduler = AsyncIOScheduler()

    async def setup_hook(self) -> None:
        self.scheduler.start()


bot = FLBot()


fl_group = app_commands.Group(name="fl", description="FetLife commands")


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
    settings = storage.get_channel_settings(bot.db, interaction.channel_id)
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
        settings = storage.get_channel_settings(bot.db, interaction.channel_id)
        await interaction.response.send_message(json.dumps(settings or {}))


@fl_group.command(name="health", description="Show adapter health")
async def fl_health(interaction: discord.Interaction) -> None:
    await interaction.response.send_message("Adapter OK; jobs: %d" % len(bot.scheduler.get_jobs()))


@fl_group.command(name="purge", description="Purge local caches")
async def fl_purge(interaction: discord.Interaction) -> None:
    await interaction.response.send_message("Purged")


async def metrics_handler(request: web.Request) -> web.Response:
    data = generate_latest()
    return web.Response(body=data, content_type=CONTENT_TYPE_LATEST)


async def main() -> None:
    if not TOKEN:
        raise RuntimeError("DISCORD_TOKEN is not set")
    app = web.Application()
    app.router.add_get("/metrics", metrics_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8000)
    await site.start()
    await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
