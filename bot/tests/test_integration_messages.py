import os
import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from bot import main, storage

pytestmark = pytest.mark.skipif(
    os.getenv("MOCK_ADAPTER") != "1", reason="requires mock adapter"
)


async def run_poll():
    db = storage.init_db("sqlite:///:memory:")
    sub_id = storage.add_subscription(db, 1, "messages", "inbox")
    channel = AsyncMock()
    channel.send = AsyncMock()
    bridge = SimpleNamespace(send_to_telegram=AsyncMock())
    main.bot.bridge = bridge
    with (
        patch.object(main.bot, "get_channel", return_value=channel),
        patch("bot.main.bot_bucket.acquire", AsyncMock()),
        patch("bot.main.bot_tokens.set"),
    ):
        await main.poll_adapter(db, sub_id, {"interval": 60})
    return channel, bridge.send_to_telegram


def test_messages_flow():
    channel, tg_send = asyncio.run(run_poll())
    channel.send.assert_called_once()
    tg_send.assert_called_once()
