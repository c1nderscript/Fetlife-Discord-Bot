from pathlib import Path
import sys
from types import SimpleNamespace
import asyncio
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bot.telegram_bridge import TelegramBridge
from unittest.mock import AsyncMock


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
        self.files = []

    async def send(self, content=None, files=None):
        self.messages.append(content)
        if files:
            self.files.extend(files)


class FakeBot:
    def __init__(self, channel_id):
        self.channel = FakeChannel()
        self.channel_id = channel_id

    def get_channel(self, cid):
        if cid == self.channel_id:
            return self.channel
        return None


def test_bridge_skips_client_creation_when_missing_credentials():
    bot = FakeBot(1)
    bridge = TelegramBridge(bot)
    assert bridge.client is None
    asyncio.run(bridge.start())  # should no-op without error


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


def test_bridge_forwards_media():
    bot = FakeBot(1)
    tg_client = FakeTelegramClient()
    bridge = TelegramBridge(
        bot,
        client=tg_client,
        config={"telegram_bridge": {"mappings": {"10": "1"}}},
    )
    asyncio.run(bridge.start())
    event = SimpleNamespace(
        chat_id=10,
        raw_text="",
        photo=True,
        file=SimpleNamespace(name="photo.jpg"),
    )

    async def dl(file):
        file.write(b"x")

    event.download_media = dl  # type: ignore[attr-defined]
    asyncio.run(tg_client.handler(event))
    assert len(bot.channel.files) == 1
    asyncio.run(bridge.stop())


def test_bridge_send_to_telegram():
    bot = FakeBot(1)
    tg_client = FakeTelegramClient()
    tg_client.send_message = AsyncMock()  # type: ignore[attr-defined]
    bridge = TelegramBridge(
        bot, client=tg_client, config={"telegram_bridge": {"mappings": {"10": "1"}}}
    )
    asyncio.run(bridge.send_to_telegram(1, "hi"))
    tg_client.send_message.assert_awaited_once_with(10, "hi")


@patch("bot.telegram_bridge.save_config")
def test_add_remove_mapping(save_cfg):
    bot = FakeBot(2)
    tg_client = FakeTelegramClient()
    bridge = TelegramBridge(
        bot, client=tg_client, config={"telegram_bridge": {"mappings": {}}}
    )
    asyncio.run(bridge.start())
    bridge.add_mapping(20, 2)
    event = SimpleNamespace(chat_id=20, raw_text="hi")
    asyncio.run(tg_client.handler(event))
    assert bot.channel.messages == ["hi"]
    bridge.remove_mapping(20)
    asyncio.run(tg_client.handler(SimpleNamespace(chat_id=20, raw_text="x")))
    assert bot.channel.messages == ["hi"]
    asyncio.run(bridge.stop())
