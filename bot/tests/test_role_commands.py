import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from bot import main


def make_interaction(*, has_perms: bool = True, role_exists: bool = True):
    interaction = AsyncMock()
    interaction.response.send_message = AsyncMock()
    guild = SimpleNamespace(
        get_role=(lambda _id: SimpleNamespace(id=_id) if role_exists else None),
        roles=[SimpleNamespace(id=1, name="role")] if role_exists else [],
    )
    interaction.guild = guild
    interaction.user.guild_permissions = SimpleNamespace(manage_roles=has_perms)
    return interaction


def assert_ephemeral(interaction):
    interaction.response.send_message.assert_called_once()
    assert interaction.response.send_message.await_args.kwargs.get("ephemeral") is True


def test_role_add_success():
    interaction = make_interaction()
    member = SimpleNamespace(add_roles=AsyncMock())
    with (
        patch("bot.main.bot_bucket.acquire", AsyncMock()),
        patch("bot.main.bot_tokens.set"),
    ):
        asyncio.run(main.role_add.callback(interaction, member, 1))
    member.add_roles.assert_awaited_once()
    interaction.response.send_message.assert_called_once_with("Role added")


def test_role_remove_success():
    interaction = make_interaction()
    member = SimpleNamespace(remove_roles=AsyncMock())
    with (
        patch("bot.main.bot_bucket.acquire", AsyncMock()),
        patch("bot.main.bot_tokens.set"),
    ):
        asyncio.run(main.role_remove.callback(interaction, member, 1))
    member.remove_roles.assert_awaited_once()
    interaction.response.send_message.assert_called_once_with("Role removed")


def test_role_permission_error():
    interaction = make_interaction(has_perms=False)
    member = SimpleNamespace(add_roles=AsyncMock())
    with (
        patch("bot.main.bot_bucket.acquire", AsyncMock()),
        patch("bot.main.bot_tokens.set"),
    ):
        asyncio.run(main.role_add.callback(interaction, member, 1))
    member.add_roles.assert_not_called()
    assert_ephemeral(interaction)


def test_role_invalid_role():
    interaction = make_interaction(role_exists=False)
    member = SimpleNamespace(add_roles=AsyncMock())
    with (
        patch("bot.main.bot_bucket.acquire", AsyncMock()),
        patch("bot.main.bot_tokens.set"),
    ):
        asyncio.run(main.role_add.callback(interaction, member, 99))
    member.add_roles.assert_not_called()
    assert_ephemeral(interaction)
