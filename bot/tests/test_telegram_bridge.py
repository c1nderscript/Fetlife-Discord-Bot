from pathlib import Path
import sys
from types import SimpleNamespace
import asyncio
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bot.telegram_bridge import TelegramBridge


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

    async def send(self, content):
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


@patch("bot.telegram_bridge.save_config")
def test_add_remove_mapping(save_cfg):
    bot = FakeBot(2)
    tg_client = FakeTelegramClient()
    bridge = TelegramBridge(bot, client=tg_client, config={"telegram_bridge": {"mappings": {}}})
    asyncio.run(bridge.start())
    bridge.add_mapping(20, 2)
    event = SimpleNamespace(chat_id=20, raw_text="hi")
    asyncio.run(tg_client.handler(event))
    assert bot.channel.messages == ["hi"]
    bridge.remove_mapping(20)
    asyncio.run(tg_client.handler(SimpleNamespace(chat_id=20, raw_text="x")))
    assert bot.channel.messages == ["hi"]
    asyncio.run(bridge.stop())
