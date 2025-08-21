import importlib
from prometheus_client import REGISTRY
import sys
import io
import json
import logging

from bot.main import JsonFormatter


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


def test_json_formatter_outputs_extra_fields():
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JsonFormatter())
    logger = logging.getLogger("test_json_formatter")
    logger.addHandler(handler)
    logger.propagate = False
    logger.info("hi", extra={"correlation_id": "123"})
    handler.flush()
    output = stream.getvalue().strip()
    logger.removeHandler(handler)
    assert json.loads(output)["correlation_id"] == "123"
