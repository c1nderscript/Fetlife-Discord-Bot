from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from pathlib import Path
from unittest.mock import AsyncMock, patch

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bot import main, storage  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures"


@dataclass
class DummyResponse:
    message: str | None = None

    async def send_message(self, content: str):
        self.message = content


@dataclass
class DummyInteraction:
    channel_id: int = 1
    response: DummyResponse = field(default_factory=DummyResponse)


async def run_poll(db, sub_id: int, items: list[dict]):
    channel = AsyncMock()
    channel.send = AsyncMock()
    with (
        patch(
            "bot.main.adapter_client.fetch_group_posts", AsyncMock(return_value=items)
        ),
        patch.object(main.bot, "get_channel", return_value=channel),
        patch.object(main.bot.scheduler, "add_job"),
        patch("bot.main.bot_bucket.acquire", AsyncMock()),
        patch("bot.main.bot_tokens.set"),
    ):
        await main.poll_adapter(db, sub_id, {"interval": 60})
    return channel


def test_fl_subscribe_group_posts_validates_target():
    main.bot.db = storage.init_db("sqlite:///:memory:")
    interaction = DummyInteraction()
    # invalid target
    with (
        patch("bot.main.bot_bucket.acquire", AsyncMock()),
        patch("bot.main.bot_tokens.set"),
    ):
        asyncio.run(main.fl_subscribe.callback(interaction, "group_posts", "user:1"))
    assert interaction.response.message == "Target must be group:<id>"
    interaction.response.message = None
    with (
        patch.object(main.bot.scheduler, "add_job") as add_job,
        patch("bot.main.bot_bucket.acquire", AsyncMock()),
        patch("bot.main.bot_tokens.set"),
    ):
        asyncio.run(main.fl_subscribe.callback(interaction, "group_posts", "group:1"))
        add_job.assert_called_once()


def test_poll_group_posts_updates_cursor_and_dedupes():
    db = storage.init_db("sqlite:///:memory:")
    sub_id = storage.add_subscription(db, 1, "group_posts", "group:1")
    item = json.loads((FIXTURES / "group_post.json").read_text())
    channel = asyncio.run(run_poll(db, sub_id, [item]))
    asyncio.run(run_poll(db, sub_id, [item]))
    channel.send.assert_called_once()
    _, ids = storage.get_cursor(db, sub_id)
    assert ids == [str(item["id"])]
