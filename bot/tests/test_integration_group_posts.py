import os
import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from bot import main, storage

pytestmark = pytest.mark.skipif(
    os.getenv("MOCK_ADAPTER") != "1", reason="requires mock adapter"
)


async def run_poll():
    db = storage.init_db("sqlite:///:memory:")
    sub_id = storage.add_subscription(db, 1, "group_posts", "group:1")
    channel = AsyncMock()
    channel.send = AsyncMock()
    with (
        patch.object(main.bot, "get_channel", return_value=channel),
        patch("bot.main.bot_bucket.acquire", AsyncMock()),
        patch("bot.main.bot_tokens.set"),
    ):
        await main.poll_adapter(db, sub_id, {"interval": 60})
    return channel


def test_group_posts_flow():
    channel = asyncio.run(run_poll())
    channel.send.assert_called_once()
