import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from bot import main


def make_interaction(*, has_perms: bool = True, role_exists: bool = True):
    interaction = AsyncMock()
    interaction.response.send_message = AsyncMock()
    guild = SimpleNamespace(
        id=1,
        get_role=(lambda _id: SimpleNamespace(id=_id) if role_exists else None),
    )
    interaction.guild = guild
    interaction.user.guild_permissions = SimpleNamespace(manage_roles=has_perms)
    return interaction


def assert_ephemeral(interaction):
    interaction.response.send_message.assert_called_once()
    assert interaction.response.send_message.await_args.kwargs.get("ephemeral") is True


def test_reactionrole_commands_registered():
    names = {c.name for c in main.reactionrole_group.walk_commands()}
    assert {"add", "remove"}.issubset(names)


def test_reactionrole_add_success():
    interaction = make_interaction()
    with (
        patch("bot.main.storage.set_reaction_role") as set_rr,
        patch("bot.main.bot_bucket.acquire", AsyncMock()),
        patch("bot.main.bot_tokens.set"),
    ):
        asyncio.run(main.reactionrole_add.callback(interaction, 1, ":smile:", 2))
    set_rr.assert_called_once_with(main.bot.db, 1, ":smile:", 2, interaction.guild.id)
    interaction.response.send_message.assert_called_once_with("Reaction role added")


def test_reactionrole_remove_success():
    interaction = make_interaction()
    with (
        patch("bot.main.storage.remove_reaction_role") as rm_rr,
        patch("bot.main.bot_bucket.acquire", AsyncMock()),
        patch("bot.main.bot_tokens.set"),
    ):
        asyncio.run(main.reactionrole_remove.callback(interaction, 1, ":smile:"))
    rm_rr.assert_called_once_with(main.bot.db, 1, ":smile:")
    interaction.response.send_message.assert_called_once_with("Reaction role removed")


def test_reactionrole_permission_error():
    interaction = make_interaction(has_perms=False)
    with (
        patch("bot.main.bot_bucket.acquire", AsyncMock()),
        patch("bot.main.bot_tokens.set"),
    ):
        asyncio.run(main.reactionrole_add.callback(interaction, 1, ":smile:", 2))
    assert_ephemeral(interaction)


def test_on_raw_reaction_add():
    payload = SimpleNamespace(message_id=1, emoji=":smile:", guild_id=1, user_id=5)
    member = SimpleNamespace(add_roles=AsyncMock())
    guild = SimpleNamespace(
        get_role=lambda _id: SimpleNamespace(id=_id),
        get_member=lambda _id: member,
    )
    with (
        patch("bot.main.storage.get_reaction_role", return_value=(2, 1)),
        patch("bot.main.bot.get_guild", return_value=guild),
        patch("bot.main.bot_bucket.acquire", AsyncMock()),
        patch("bot.main.bot_tokens.set"),
    ):
        asyncio.run(main.on_raw_reaction_add(payload))
    member.add_roles.assert_awaited_once()


def test_on_raw_reaction_remove():
    payload = SimpleNamespace(message_id=1, emoji=":smile:", guild_id=1, user_id=5)
    member = SimpleNamespace(remove_roles=AsyncMock())
    guild = SimpleNamespace(
        get_role=lambda _id: SimpleNamespace(id=_id),
        get_member=lambda _id: member,
    )
    with (
        patch("bot.main.storage.get_reaction_role", return_value=(2, 1)),
        patch("bot.main.bot.get_guild", return_value=guild),
        patch("bot.main.bot_bucket.acquire", AsyncMock()),
        patch("bot.main.bot_tokens.set"),
    ):
        asyncio.run(main.on_raw_reaction_remove(payload))
    member.remove_roles.assert_awaited_once()
