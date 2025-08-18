import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from bot import main, birthday


def make_interaction():
    interaction = AsyncMock()
    interaction.user = SimpleNamespace(id=42)
    interaction.guild_id = 1
    interaction.client = main.bot
    interaction.response.send_message = AsyncMock()
    return interaction


def test_set_creates_entry():
    interaction = make_interaction()
    asyncio.run(
        birthday.set_birthday.callback(interaction, "2000-01-02", "UTC", False, None)
    )
    row = main.bot.db.query(birthday.Birthday).filter_by(user_id=42, guild_id=1).first()
    assert row is not None


def test_list_and_remove():
    interaction = make_interaction()
    asyncio.run(birthday.list_birthdays.callback(interaction))
    interaction.response.send_message.assert_called()
    asyncio.run(birthday.remove_birthday.callback(interaction))
    row = main.bot.db.query(birthday.Birthday).filter_by(user_id=42, guild_id=1).first()
    assert row is None
