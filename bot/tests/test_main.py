import importlib
from prometheus_client import REGISTRY
import sys


def test_flbot_without_telegram(monkeypatch):
    monkeypatch.delenv("TELEGRAM_API_ID", raising=False)
    monkeypatch.delenv("TELEGRAM_API_HASH", raising=False)
    monkeypatch.setenv("DISCORD_TOKEN", "x")
    for collector in list(REGISTRY._collector_to_names):
        REGISTRY.unregister(collector)
    sys.modules.pop("bot.main", None)
    m = importlib.import_module("bot.main")
    m.main(require_env=False)
    bot = m.FLBot()
    assert bot.bridge is None
