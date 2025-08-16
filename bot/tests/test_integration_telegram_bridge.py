import os
import asyncio
from types import SimpleNamespace

import pytest

from bot.telegram_bridge import TelegramBridge

pytestmark = pytest.mark.skipif(
    os.getenv("MOCK_ADAPTER") != "1", reason="requires mock adapter"
)


class FakeTelegramClient:
    def __init__(self):
        self.handler = None

    def add_event_handler(self, handler, *_):
        self.handler = handler

    async def start(self):
        return self

    async def disconnect(self):
        return None


class FakeChannel:
    def __init__(self):
        self.messages = []

    async def send(self, content=None, files=None):
        self.messages.append(content)


class FakeBot:
    def __init__(self, channel_id):
        self.channel = FakeChannel()
        self.channel_id = channel_id

    def get_channel(self, cid):
        if cid == self.channel_id:
            return self.channel
        return None


def test_bridge_forwards_messages():
    bot = FakeBot(1)
    tg_client = FakeTelegramClient()
    bridge = TelegramBridge(
        bot,
        client=tg_client,
        config={"telegram_bridge": {"mappings": {"10": "1"}}},
    )
    asyncio.run(bridge.start())
    event = SimpleNamespace(chat_id=10, raw_text="hello")
    asyncio.run(tg_client.handler(event))
    assert bot.channel.messages == ["hello"]
    asyncio.run(bridge.stop())
