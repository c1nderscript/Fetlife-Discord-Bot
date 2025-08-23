import asyncio  # for scheduling sleeps
from datetime import datetime
from typing import cast

import discord
import logging
from prometheus_client import Counter

from . import models


logger = logging.getLogger(__name__)


messages_deleted = Counter("timed_messages_deleted_total", "Timed messages deleted")


async def _delete_once(bot: discord.Client) -> None:
    now = datetime.utcnow()
    expired = (
        bot.db.query(models.TimedMessage)
        .filter(models.TimedMessage.delete_at <= now)
        .all()
    )
    for msg in expired:
        channel = bot.get_channel(msg.channel_id)
        if channel:
            try:
                fetched = await cast(discord.abc.Messageable, channel).fetch_message(
                    msg.message_id
                )
                await fetched.delete()
                messages_deleted.inc()
            except Exception:
                logger.exception("Failed to delete timed message %s", msg.message_id)
        bot.db.delete(msg)
    bot.db.commit()


async def delete_expired_messages(bot: discord.Client, interval: int = 5) -> None:
    await bot.wait_until_ready()
    while not bot.is_closed():
        await _delete_once(bot)
        await asyncio.sleep(interval)
