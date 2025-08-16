import asyncio
import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bot import main, storage  # noqa: E402

if main.bot.bridge is None:
    main.bot.bridge = SimpleNamespace()
if not hasattr(main.bot.bridge, "send_to_telegram"):
    main.bot.bridge.send_to_telegram = AsyncMock()

FIXTURES = Path(__file__).parent / "fixtures"


async def run_poll(db, sub_id: int, items: list[dict]):
    channel = AsyncMock()
    channel.send = AsyncMock()
    with (
        patch("bot.main.adapter_client.fetch_messages", AsyncMock(return_value=items)),
        patch.object(main.bot, "get_channel", return_value=channel),
        patch.object(main.bot.bridge, "send_to_telegram", AsyncMock()) as tg_send,
        patch.object(main.bot.scheduler, "add_job"),
        patch("bot.main.bot_bucket.acquire", AsyncMock()),
        patch("bot.main.bot_tokens.set"),
    ):
        await main.poll_adapter(db, sub_id, {"interval": 60})
    return channel, tg_send


def test_poll_messages_updates_cursor_and_relays():
    db = storage.init_db("sqlite:///:memory:")
    sub_id = storage.add_subscription(db, 1, "messages", "inbox")
    item = json.loads((FIXTURES / "message.json").read_text())
    channel, tg_send = asyncio.run(run_poll(db, sub_id, [item]))
    channel.send.assert_called_once()
    tg_send.assert_called_once()
    _, ids = storage.get_cursor(db, sub_id)
    assert ids == [str(item["id"])]
