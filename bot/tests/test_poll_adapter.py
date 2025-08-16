from pathlib import Path
import asyncio
import sys
import os
from unittest.mock import AsyncMock, patch

import aiohttp
import discord
import time
from types import SimpleNamespace

os.environ.setdefault("TELEGRAM_API_ID", "1")
os.environ.setdefault("TELEGRAM_API_HASH", "hash")
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from bot import main, storage, models  # noqa: E402


async def run_poll(
    db, sub_id, items, data, fetch_fn="fetch_events", error=False, channel=None
):
    fetch_mock = AsyncMock(return_value=items)
    if error:
        fetch_mock = AsyncMock(side_effect=aiohttp.ClientError())
    if channel is None:
        channel = AsyncMock(spec=discord.abc.Messageable)
        channel.send = AsyncMock()
    with (
        patch(f"bot.main.adapter_client.{fetch_fn}", fetch_mock),
        patch.object(main.bot, "get_channel", return_value=channel),
        patch.object(main.bot.scheduler, "add_job"),
        patch("bot.main.bot_bucket.acquire", AsyncMock()),
        patch("bot.main.bot_tokens.set"),
    ):
        await main.poll_adapter(db, sub_id, data)
    return channel


def test_poll_adapter_dedupes_and_updates_cursor():
    db = storage.init_db("sqlite:///:memory:")
    sub_id = storage.add_subscription(db, 1, "events", "cities/1")
    channel = asyncio.run(
        run_poll(
            db,
            sub_id,
            [
                {
                    "id": "1",
                    "title": "t",
                    "link": "l",
                    "time": "2024-01-01T00:00:00Z",
                    "city": "X",
                }
            ],
            {"interval": 60},
            channel=AsyncMock(send=AsyncMock()),
        )
    )
    asyncio.run(
        run_poll(
            db,
            sub_id,
            [
                {
                    "id": "1",
                    "title": "t",
                    "link": "l",
                    "time": "2024-01-01T00:00:00Z",
                    "city": "X",
                }
            ],
            {"interval": 60},
            channel=channel,
        )
    )
    assert db.query(models.RelayLog).count() == 1
    _, ids = storage.get_cursor(db, sub_id)
    assert ids == ["1"]
    assert channel.send.call_count == 1
    event = db.query(models.Event).filter_by(fl_id="1").one()
    assert event.title == "t"


def test_poll_adapter_backoff_on_http_error():
    db = storage.init_db("sqlite:///:memory:")
    sub_id = storage.add_subscription(db, 1, "events", "cities/1")
    data = {"interval": 60}
    with (
        patch(
            "bot.main.adapter_client.fetch_events",
            AsyncMock(side_effect=aiohttp.ClientError()),
        ),
        patch.object(
            main.bot.scheduler,
            "add_job",
        ) as add_job,
        patch("bot.main.bot_bucket.acquire", AsyncMock()),
        patch("bot.main.bot_tokens.set"),
    ):
        asyncio.run(main.poll_adapter(db, sub_id, data))
    assert data["backoff"] == 120
    add_job.assert_called_once()


def test_poll_adapter_writings():
    db = storage.init_db("sqlite:///:memory:")
    sub_id = storage.add_subscription(db, 1, "writings", "1")
    channel = asyncio.run(
        run_poll(
            db,
            sub_id,
            [
                {
                    "id": "1",
                    "title": "t",
                    "link": "l",
                    "published": "now",
                }
            ],
            {"interval": 60},
            fetch_fn="fetch_writings",
        )
    )
    assert db.query(models.RelayLog).count() == 1
    channel.send.assert_called_once()


def test_poll_adapter_pauses_and_notifies_after_failures():
    main.bot.sub_status.clear()
    db = storage.init_db("sqlite:///:memory:")
    sub_id = storage.add_subscription(db, 1, "events", "cities/1")
    data = {"interval": 60}
    channel = AsyncMock()
    channel.send = AsyncMock()
    for _ in range(main.MAX_FAILURES):
        asyncio.run(run_poll(db, sub_id, [], data, error=True, channel=channel))
    assert data["failures"] == main.MAX_FAILURES
    assert "paused_until" in data
    channel.send.assert_called_once()
    assert sub_id in main.bot.sub_status


def test_poll_adapter_resumes_after_cooldown():
    main.bot.sub_status.clear()
    db = storage.init_db("sqlite:///:memory:")
    sub_id = storage.add_subscription(db, 1, "events", "cities/1")
    data = {"interval": 60}
    channel = AsyncMock()
    channel.send = AsyncMock()
    for _ in range(main.MAX_FAILURES):
        asyncio.run(run_poll(db, sub_id, [], data, error=True, channel=channel))
    data["paused_until"] = time.time() - 1
    asyncio.run(run_poll(db, sub_id, [], data, channel=channel))
    assert data["failures"] == 0
    assert "paused_until" not in data
    assert main.bot.sub_status[sub_id]["failures"] == 0


def test_fl_health_reports_and_resumes():
    main.bot.sub_status.clear()
    db = storage.init_db("sqlite:///:memory:")
    sub_id = storage.add_subscription(db, 1, "events", "cities/1")
    data = {"interval": 60}
    channel = AsyncMock()
    channel.send = AsyncMock()
    for _ in range(main.MAX_FAILURES):
        asyncio.run(run_poll(db, sub_id, [], data, error=True, channel=channel))
    interaction = AsyncMock()
    interaction.response.send_message = AsyncMock()
    with (
        patch("bot.main.bot_bucket.acquire", AsyncMock()),
        patch("bot.main.bot_tokens.set"),
        patch.object(main.bot.scheduler, "get_jobs", return_value=[]),
    ):
        asyncio.run(main.fl_health.callback(interaction))
    msg = interaction.response.send_message.call_args[0][0]
    assert str(sub_id) in msg and "paused" in msg
    job = SimpleNamespace(args=[db, sub_id, data])
    interaction2 = AsyncMock()
    interaction2.response.send_message = AsyncMock()
    with (
        patch("bot.main.bot_bucket.acquire", AsyncMock()),
        patch("bot.main.bot_tokens.set"),
        patch.object(main.bot.scheduler, "get_job", return_value=job),
        patch.object(main.bot.scheduler, "add_job") as add_job,
    ):
        asyncio.run(main.fl_health.callback(interaction2, resume=sub_id))
    assert data["failures"] == 0
    assert "paused_until" not in data
    add_job.assert_called_once()
