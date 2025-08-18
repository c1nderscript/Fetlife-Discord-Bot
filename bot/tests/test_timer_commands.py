import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from datetime import datetime, timedelta

from bot import main, tasks, models


def make_interaction():
    interaction = AsyncMock()
    interaction.channel_id = 1
    interaction.channel = SimpleNamespace(id=1)
    interaction.response.send_message = AsyncMock()
    interaction.original_response = AsyncMock(
        return_value=SimpleNamespace(id=10, channel=SimpleNamespace(id=1))
    )
    return interaction


def test_timer_schedules_message():
    interaction = make_interaction()
    with (
        patch("bot.main.storage.get_channel_settings", return_value={}),
        patch("bot.main.bot_bucket.acquire", AsyncMock()),
        patch("bot.main.bot_tokens.set"),
    ):
        asyncio.run(main.timer.callback(interaction, "hi", 5))
    tm = (
        main.bot.db.query(models.TimedMessage)
        .filter(models.TimedMessage.message_id == 10)
        .first()
    )
    assert tm is not None


def test_autodelete_sets_channel_setting():
    interaction = make_interaction()
    with (
        patch("bot.main.storage.set_channel_settings") as set_settings,
        patch("bot.main.bot_bucket.acquire", AsyncMock()),
        patch("bot.main.bot_tokens.set"),
    ):
        asyncio.run(main.autodelete.callback(interaction, 5))
    set_settings.assert_called_once_with(main.bot.db, 1, autodelete=5)


def test_delete_once_removes_expired():
    main.bot.db.add(
        models.TimedMessage(
            message_id=99,
            channel_id=1,
            delete_at=datetime.utcnow() - timedelta(seconds=1),
        )
    )
    main.bot.db.commit()
    channel = SimpleNamespace(
        fetch_message=AsyncMock(return_value=SimpleNamespace(delete=AsyncMock()))
    )
    bot = SimpleNamespace(
        db=main.bot.db,
        get_channel=lambda _id: channel,
        is_closed=lambda: True,
        wait_until_ready=AsyncMock(),
    )
    asyncio.run(tasks._delete_once(bot))
    row = (
        main.bot.db.query(models.TimedMessage)
        .filter(models.TimedMessage.message_id == 99)
        .first()
    )
    assert row is None
