import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import asyncio
from unittest.mock import patch

from bot.adapter_client import (
    fetch_events,
    fetch_group_posts,
    fetch_writings,
    login,
)


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

    def get(self, url, params=None, headers=None):
        return DummyResp()

    def post(self, url, json=None, headers=None):
        return DummyResp()


def test_fetch_events_mocked():
    with patch("aiohttp.ClientSession", return_value=DummySession()):
        events = asyncio.run(fetch_events("http://adapter", "cities/1", account_id=1))
    assert events == [{"id": 1}]


def test_fetch_writings_mocked():
    with patch("aiohttp.ClientSession", return_value=DummySession()):
        writings = asyncio.run(fetch_writings("http://adapter", "1", account_id=1))
    assert writings == [{"id": 1}]


def test_fetch_group_posts_mocked():
    with patch("aiohttp.ClientSession", return_value=DummySession()):
        posts = asyncio.run(fetch_group_posts("http://adapter", "1", account_id=1))
    assert posts == [{"id": 1}]


def test_login_mocked():
    with patch("aiohttp.ClientSession", return_value=DummySession()):
        resp = asyncio.run(login("http://adapter", "u", "p", account_id=1))
    assert resp == [{"id": 1}]

