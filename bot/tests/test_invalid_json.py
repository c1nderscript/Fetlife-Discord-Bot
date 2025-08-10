import asyncio
from dataclasses import dataclass, field
from unittest.mock import patch

from bot import main, storage


@dataclass
class DummyResponse:
    message: str | None = None

    async def send_message(self, content: str, **kwargs):
        self.message = content


@dataclass
class DummyInteraction:
    channel_id: int = 1
    response: DummyResponse = field(default_factory=DummyResponse)


def test_fl_subscribe_invalid_json():
    async def run():
        main.bot.db = storage.init_db("sqlite:///:memory:")
        interaction = DummyInteraction()
        with patch.object(main.bot.scheduler, "add_job") as add_job:
            await main.fl_subscribe.callback(interaction, "events", "cities/1", filters="{bad")
            add_job.assert_not_called()
        return interaction

    interaction = asyncio.run(run())
    assert interaction.response.message == "Invalid JSON for filters"
    assert not storage.list_subscriptions(main.bot.db, interaction.channel_id)
