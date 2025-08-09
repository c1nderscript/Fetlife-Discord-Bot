import asyncio
from dataclasses import dataclass
from unittest.mock import patch

from bot import storage
from bot import main


@dataclass
class DummyResponse:
    message: str | None = None

    async def send_message(self, content: str):
        self.message = content


@dataclass
class DummyInteraction:
    channel_id: int = 1
    response: DummyResponse = DummyResponse()


async def run_flow():
    main.fetlife_requests._value.set(0)
    main.bot.db = storage.init_db("sqlite:///:memory:")
    interaction = DummyInteraction()
    with patch.object(main.bot.scheduler, "add_job"):
        await main.fl_subscribe(interaction, "events", "cities/1")
    await main.poll_adapter(main.bot.db, 1, {"interval": 60})
    return interaction


def test_subscribe_flow():
    interaction = asyncio.run(run_flow())
    assert interaction.response.message.startswith("Subscribed with id")
    assert main.fetlife_requests._value.get() == 1
