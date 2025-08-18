import asyncio
from types import SimpleNamespace
import sys
from pathlib import Path
import pytest
from discord import app_commands

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bot import main


def make_interaction():
    return SimpleNamespace(
        guild_id=1,
        guild=SimpleNamespace(id=1),
        user=SimpleNamespace(id=1),
        command=SimpleNamespace(qualified_name="role add"),
    )


def test_admin_rate_limit():
    main.bot.admin_cooldowns.clear()
    main.bot.config = {"defaults": {"admin_command_rate": 1, "admin_command_per": 60}}
    interaction = make_interaction()
    asyncio.run(main.admin_rate_limit(interaction))
    with pytest.raises(app_commands.CommandOnCooldown):
        asyncio.run(main.admin_rate_limit(interaction))
