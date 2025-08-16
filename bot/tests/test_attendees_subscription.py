from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bot import main, storage, models  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures"


async def run_poll(db, sub_id: int, items: list[dict]):
    channel = AsyncMock()
    channel.send = AsyncMock()
    with (
        patch("bot.main.adapter_client.fetch_attendees", AsyncMock(return_value=items)),
        patch.object(main.bot, "get_channel", return_value=channel),
        patch.object(main.bot.scheduler, "add_job"),
        patch("bot.main.bot_bucket.acquire", AsyncMock()),
        patch("bot.main.bot_tokens.set"),
    ):
        await main.poll_adapter(db, sub_id, {"interval": 60})
    return channel


def test_poll_attendees_updates_cursor_and_sends_message():
    db = storage.init_db("sqlite:///:memory:")
    sub_id = storage.add_subscription(db, 1, "attendees", "event:1")
    items = json.loads((FIXTURES / "event_attendees.json").read_text())
    channel = asyncio.run(run_poll(db, sub_id, items))
    channel.send.assert_called_once()
    _, ids = storage.get_cursor(db, sub_id)
    assert ids == [str(items[0]["id"])]
    profile = db.query(models.Profile).filter_by(fl_id=str(items[0]["id"]))
    assert profile.one().nickname == items[0]["nickname"]
    event = db.query(models.Event).filter_by(fl_id="1").one()
    rsvp = db.get(models.RSVP, (event.id, str(items[0]["id"])))
    assert rsvp.status == items[0]["status"]
