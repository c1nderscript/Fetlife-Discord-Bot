import os
import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

os.environ.setdefault("TELEGRAM_API_ID", "1")
os.environ.setdefault("TELEGRAM_API_HASH", "hash")

from bot import main

if main.bot.bridge is None:
    main.bot.bridge = SimpleNamespace(
        add_mapping=AsyncMock(), remove_mapping=AsyncMock()
    )


def make_interaction():
    interaction = AsyncMock()
    interaction.response.send_message = AsyncMock()
    interaction.user.guild_permissions = SimpleNamespace(administrator=False)
    return interaction


def assert_ephemeral(interaction):
    interaction.response.send_message.assert_called_once()
    assert interaction.response.send_message.await_args.kwargs.get("ephemeral") is True


def test_fl_account_add_unauthorized():
    interaction = make_interaction()
    with (
        patch("bot.main.bot_bucket.acquire", AsyncMock()),
        patch("bot.main.bot_tokens.set"),
        patch("bot.main.storage.add_account") as add_account,
        patch("bot.main.adapter_client.login") as login,
    ):
        asyncio.run(main.fl_account_add.callback(interaction, "user", "pass"))
    add_account.assert_not_called()
    login.assert_not_called()
    assert_ephemeral(interaction)


def test_fl_account_remove_unauthorized():
    interaction = make_interaction()
    with (
        patch("bot.main.bot_bucket.acquire", AsyncMock()),
        patch("bot.main.bot_tokens.set"),
        patch("bot.main.storage.remove_account") as remove_account,
    ):
        asyncio.run(main.fl_account_remove.callback(interaction, 1))
    remove_account.assert_not_called()
    assert_ephemeral(interaction)


def test_fl_telegram_add_unauthorized():
    interaction = make_interaction()
    channel = SimpleNamespace(id=123)
    with (
        patch("bot.main.bot_bucket.acquire", AsyncMock()),
        patch("bot.main.bot_tokens.set"),
        patch("bot.main.save_config"),
        patch.object(main.bot.bridge, "add_mapping") as add_mapping,
    ):
        asyncio.run(main.fl_telegram_add.callback(interaction, "1", channel))
    add_mapping.assert_not_called()
    assert_ephemeral(interaction)


def test_fl_telegram_remove_unauthorized():
    interaction = make_interaction()
    with (
        patch("bot.main.bot_bucket.acquire", AsyncMock()),
        patch("bot.main.bot_tokens.set"),
        patch("bot.main.save_config"),
        patch.object(main.bot.bridge, "remove_mapping") as remove_mapping,
    ):
        asyncio.run(main.fl_telegram_remove.callback(interaction, "1"))
    remove_mapping.assert_not_called()
    assert_ephemeral(interaction)


def test_fl_purge_unauthorized():
    interaction = make_interaction()
    with (
        patch("bot.main.bot_bucket.acquire", AsyncMock()),
        patch("bot.main.bot_tokens.set"),
    ):
        asyncio.run(main.fl_purge.callback(interaction))
    assert_ephemeral(interaction)
