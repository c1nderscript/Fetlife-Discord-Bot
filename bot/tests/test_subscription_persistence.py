import asyncio
import importlib
import sys
from pathlib import Path

from prometheus_client import REGISTRY

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

asyncio.set_event_loop(asyncio.new_event_loop())

from bot import storage


def _reload_main():
    for collector in list(REGISTRY._collector_to_names):
        REGISTRY.unregister(collector)
    sys.modules.pop("bot.main", None)
    return importlib.import_module("bot.main")


def test_subscriptions_persist_across_restarts(tmp_path, monkeypatch):
    db_file = tmp_path / "test.db"
    db_url = f"sqlite:///{db_file}"
    monkeypatch.setenv("DATABASE_URL", db_url)
    monkeypatch.setenv("DISCORD_TOKEN", "x")

    db = storage.init_db(db_url)
    sub_id = storage.add_subscription(db, 1, "events", "cities/1")
    db.close()

    main = _reload_main()
    bot1 = main.FLBot()
    main.bot = bot1
    asyncio.run(bot1.setup_hook())
    assert str(sub_id) in [job.id for job in bot1.scheduler.get_jobs()]

    main = _reload_main()
    bot2 = main.FLBot()
    main.bot = bot2
    asyncio.run(bot2.setup_hook())
    assert str(sub_id) in [job.id for job in bot2.scheduler.get_jobs()]
