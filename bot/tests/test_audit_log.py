import asyncio
from types import SimpleNamespace

from bot import main, models
from bot.audit import log_action


@log_action("dummy", target_param="target")
async def dummy(interaction, target: str) -> None:
    pass


def test_log_action_inserts():
    interaction = SimpleNamespace(user=SimpleNamespace(id=1))
    asyncio.run(dummy(interaction, target="x"))
    row = main.bot.db.query(models.AuditLog).first()
    assert row is not None
    assert row.user_id == 1
    assert row.action == "dummy"
    assert row.target == "x"
