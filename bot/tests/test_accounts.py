import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import asyncio
from unittest.mock import AsyncMock, patch

from bot import storage, models, main


def setup_db():
    return storage.init_db("sqlite:///:memory:")


def test_add_list_remove_account():
    db = setup_db()
    aid = storage.add_account(db, "u", "p")
    accounts = list(storage.list_accounts(db))
    assert accounts == [(aid, "u")]
    storage.remove_account(db, aid)
    assert list(storage.list_accounts(db)) == []


def test_subscription_account_selection():
    db = setup_db()
    a1 = storage.add_account(db, "u1", "p1")
    sub_id = storage.add_subscription(db, 1, "events", "t", account_id=a1)
    sub = db.get(models.Subscription, sub_id)
    assert sub.account_id == a1


def test_poll_adapter_uses_correct_account():
    db = setup_db()
    a1 = storage.add_account(db, "u1", "p1")
    a2 = storage.add_account(db, "u2", "p2")
    s1 = storage.add_subscription(db, 1, "events", "loc1", account_id=a1)
    s2 = storage.add_subscription(db, 1, "events", "loc2", account_id=a2)

    channel = AsyncMock()
    channel.send = AsyncMock()

    fetch_mock = AsyncMock(return_value=[])
    with patch("bot.main.adapter_client.fetch_events", fetch_mock), patch.object(
        main.bot, "get_channel", return_value=channel
    ), patch.object(main.bot.scheduler, "add_job"), patch(
        "bot.main.bot_bucket.acquire", AsyncMock()
    ), patch("bot.main.bot_tokens.set"):
        asyncio.run(main.poll_adapter(db, s1, {"interval": 60}))
        asyncio.run(main.poll_adapter(db, s2, {"interval": 60}))

    assert fetch_mock.call_args_list[0].kwargs["account_id"] == a1
    assert fetch_mock.call_args_list[1].kwargs["account_id"] == a2
