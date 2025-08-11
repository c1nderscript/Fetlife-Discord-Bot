from pathlib import Path
import asyncio
import sys
from unittest.mock import AsyncMock, patch

import aiohttp

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from bot import main, storage, models  # noqa: E402


async def run_poll(
    db, sub_id, items, data, fetch_fn="fetch_events", error=False, channel=None
):
    fetch_mock = AsyncMock(return_value=items)
    if error:
        fetch_mock = AsyncMock(side_effect=aiohttp.ClientError())
    if channel is None:
        channel = AsyncMock()
        channel.send = AsyncMock()
    with patch(f"bot.main.adapter_client.{fetch_fn}", fetch_mock), patch.object(
        main.bot, "get_channel", return_value=channel
    ), patch.object(main.bot.scheduler, "add_job"), patch(
        "bot.main.bot_bucket.acquire", AsyncMock()
    ), patch("bot.main.bot_tokens.set"):
        await main.poll_adapter(db, sub_id, data)
    return channel


def test_poll_adapter_dedupes_and_updates_cursor():
    db = storage.init_db("sqlite:///:memory:")
    sub_id = storage.add_subscription(db, 1, "events", "cities/1")
    channel = asyncio.run(
        run_poll(
            db,
            sub_id,
            [{"id": "1", "title": "t", "link": "l", "time": "now"}],
            {"interval": 60},
            channel=AsyncMock(send=AsyncMock()),
        )
    )
    asyncio.run(
        run_poll(
            db,
            sub_id,
            [{"id": "1", "title": "t", "link": "l", "time": "now"}],
            {"interval": 60},
            channel=channel,
        )
    )
    assert db.query(models.RelayLog).count() == 1
    _, ids = storage.get_cursor(db, sub_id)
    assert ids == ["1"]
    assert channel.send.call_count == 1


def test_poll_adapter_backoff_on_http_error():
    db = storage.init_db("sqlite:///:memory:")
    sub_id = storage.add_subscription(db, 1, "events", "cities/1")
    data = {"interval": 60}
    with patch(
        "bot.main.adapter_client.fetch_events",
        AsyncMock(side_effect=aiohttp.ClientError()),
    ), patch.object(
        main.bot.scheduler,
        "add_job",
    ) as add_job, patch(
        "bot.main.bot_bucket.acquire", AsyncMock()
    ), patch("bot.main.bot_tokens.set"):
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
