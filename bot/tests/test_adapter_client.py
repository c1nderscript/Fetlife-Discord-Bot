import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import asyncio
from unittest.mock import patch

from bot.adapter_client import fetch_events


class DummyResp:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def json(self):
        return [{"id": 1}]

    def raise_for_status(self):
        pass


class DummySession:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    def get(self, url, params=None):
        return DummyResp()


def test_fetch_events_mocked():
    with patch("aiohttp.ClientSession", return_value=DummySession()):
        events = asyncio.run(fetch_events("http://adapter", "cities/1"))
    assert events == [{"id": 1}]
