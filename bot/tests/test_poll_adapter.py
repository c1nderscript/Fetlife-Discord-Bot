import asyncio
from pathlib import Path
import sys
from unittest.mock import AsyncMock, patch

import aiohttp

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from bot import main, storage, models  # noqa: E402


async def run_poll(db, sub_id, events, data, error=False):
    fetch_mock = AsyncMock(return_value=events)
    if error:
        fetch_mock = AsyncMock(side_effect=aiohttp.ClientError())
    with patch("bot.main.adapter_client.fetch_events", fetch_mock):
        with patch.object(
            main.bot.scheduler,
            "add_job",
        ):
            await main.poll_adapter(db, sub_id, data)


def test_poll_adapter_dedupes_and_updates_cursor():
    db = storage.init_db("sqlite:///:memory:")
    sub_id = storage.add_subscription(db, 1, "events", "cities/1")
    asyncio.run(run_poll(db, sub_id, [{"id": "1"}], {"interval": 60}))
    asyncio.run(run_poll(db, sub_id, [{"id": "1"}], {"interval": 60}))
    assert db.query(models.RelayLog).count() == 1
    _, ids = storage.get_cursor(db, sub_id)
    assert ids == ["1"]


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
    ) as add_job:
        asyncio.run(main.poll_adapter(db, sub_id, data))
    assert data["backoff"] == 120
    add_job.assert_called_once()
