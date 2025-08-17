import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from bot import main


def make_interaction(*, has_perms: bool = True):
    interaction = AsyncMock()
    interaction.response.send_message = AsyncMock()
    guild = SimpleNamespace(create_text_channel=AsyncMock())
    interaction.guild = guild
    interaction.user.guild_permissions = SimpleNamespace(manage_channels=has_perms)
    return interaction


def assert_ephemeral(interaction):
    interaction.response.send_message.assert_called_once()
    assert interaction.response.send_message.await_args.kwargs.get("ephemeral") is True


def test_channel_create_success():
    interaction = make_interaction()
    with (
        patch("bot.main.bot_bucket.acquire", AsyncMock()),
        patch("bot.main.bot_tokens.set"),
    ):
        asyncio.run(main.channel_create.callback(interaction, "new"))
    interaction.guild.create_text_channel.assert_awaited_once_with("new")
    interaction.response.send_message.assert_called_once_with("Channel created")


def test_channel_delete_success():
    interaction = make_interaction()
    channel = SimpleNamespace(delete=AsyncMock())
    with (
        patch("bot.main.bot_bucket.acquire", AsyncMock()),
        patch("bot.main.bot_tokens.set"),
    ):
        asyncio.run(main.channel_delete.callback(interaction, channel))
    channel.delete.assert_awaited_once()
    interaction.response.send_message.assert_called_once_with("Channel deleted")


def test_channel_rename_success():
    interaction = make_interaction()
    channel = SimpleNamespace(edit=AsyncMock())
    with (
        patch("bot.main.bot_bucket.acquire", AsyncMock()),
        patch("bot.main.bot_tokens.set"),
    ):
        asyncio.run(main.channel_rename.callback(interaction, channel, "renamed"))
    channel.edit.assert_awaited_once_with(name="renamed")
    interaction.response.send_message.assert_called_once_with("Channel renamed")


def test_channel_create_permission_error():
    interaction = make_interaction(has_perms=False)
    with (
        patch("bot.main.bot_bucket.acquire", AsyncMock()),
        patch("bot.main.bot_tokens.set"),
    ):
        asyncio.run(main.channel_create.callback(interaction, "new"))
    interaction.guild.create_text_channel.assert_not_called()
    assert_ephemeral(interaction)
