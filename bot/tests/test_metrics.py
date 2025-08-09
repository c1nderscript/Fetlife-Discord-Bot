import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bot import storage  # noqa: E402
from bot.main import (  # noqa: E402
    duplicates_suppressed,
    fetlife_requests,
    poll_adapter,
)


def test_poll_metrics():
    fetlife_requests._value.set(0)
    duplicates_suppressed._value.set(0)
    db = storage.init_db("sqlite:///:memory:")
    sub_id = storage.add_subscription(db, 1, "events", "target")

    async def run() -> None:
        await poll_adapter(db, sub_id, {})
        await poll_adapter(db, sub_id, {})

    asyncio.run(run())

    assert fetlife_requests._value.get() == 2
    assert duplicates_suppressed._value.get() == 1
