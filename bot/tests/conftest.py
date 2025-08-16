import os
import pytest
from prometheus_client import REGISTRY

os.environ.setdefault("DISCORD_TOKEN", "test-token")
os.environ.setdefault("ADAPTER_AUTH_TOKEN", "test-adapter-token")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")


@pytest.fixture(autouse=True)
def _env(monkeypatch, tmp_path):
    monkeypatch.setenv("DISCORD_TOKEN", os.environ["DISCORD_TOKEN"])
    monkeypatch.setenv("ADAPTER_AUTH_TOKEN", os.environ["ADAPTER_AUTH_TOKEN"])
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path}/test.db")
    yield
    for collector in list(REGISTRY._collector_to_names):
        REGISTRY.unregister(collector)
