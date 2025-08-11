from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bot import main, storage  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures"


async def run_poll(db, sub_id: int, items: list[dict]):
    channel = AsyncMock()
    channel.send = AsyncMock()
    with patch(
        "bot.main.adapter_client.fetch_writings", AsyncMock(return_value=items)
    ), patch.object(main.bot, "get_channel", return_value=channel), patch.object(
        main.bot.scheduler, "add_job"
    ), patch("bot.main.bot_bucket.acquire", AsyncMock()), patch(
        "bot.main.bot_tokens.set"
    ):
        await main.poll_adapter(db, sub_id, {"interval": 60})
    return channel


def test_poll_writings_updates_cursor_and_sends_message():
    db = storage.init_db("sqlite:///:memory:")
    sub_id = storage.add_subscription(db, 1, "writings", "1")
    item = json.loads((FIXTURES / "writing.json").read_text())
    channel = asyncio.run(run_poll(db, sub_id, [item]))
    channel.send.assert_called_once()
    _, ids = storage.get_cursor(db, sub_id)
    assert ids == [str(item["id"])]
