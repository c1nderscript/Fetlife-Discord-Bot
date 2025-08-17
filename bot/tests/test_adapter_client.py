import asyncio
import logging
import os
from unittest.mock import patch

from bot.adapter_client import (
    fetch_events,
    fetch_attendees,
    fetch_group_posts,
    fetch_writings,
    fetch_messages,
    login,
    login_adapter,
    close_session,
)


class DummyResp:
    def __init__(self, data, status: int = 200):
        self._data = data
        self.status = status

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def json(self):
        return self._data

    def raise_for_status(self):
        pass


class DummySession:
    def __init__(self, data):
        self.data = data
        self.headers = None
        self.closed = False

    def get(self, url, params=None, headers=None):
        self.headers = headers
        return DummyResp(self.data)

    def post(self, url, json=None, headers=None):
        self.headers = headers
        return DummyResp(self.data)

    async def close(self):
        self.closed = True


def test_fetch_events_mocked():
    data = [{"id": 1, "title": "t", "link": "l", "time": "now"}]
    sess = DummySession(data)
    events = asyncio.run(
        fetch_events("http://adapter", "cities/1", account_id=1, session=sess)
    )
    assert events == data


def test_fetch_writings_mocked():
    data = [{"id": 1, "title": "t", "link": "l", "published": "now"}]
    sess = DummySession(data)
    writings = asyncio.run(
        fetch_writings("http://adapter", "1", account_id=1, session=sess)
    )
    assert writings == data


def test_fetch_group_posts_mocked():
    data = [{"id": 1, "title": "t", "link": "l", "published": "now"}]
    sess = DummySession(data)
    posts = asyncio.run(
        fetch_group_posts("http://adapter", "1", account_id=1, session=sess)
    )
    assert posts == data


def test_fetch_attendees_mocked():
    data = [{"id": 1, "nickname": "n", "status": "going", "comment": None}]
    sess = DummySession(data)
    attendees = asyncio.run(
        fetch_attendees("http://adapter", "1", account_id=1, session=sess)
    )
    assert attendees == data


def test_fetch_messages_mocked():
    data = [{"id": 1, "sender": "s", "text": "hi", "sent": "now"}]
    sess = DummySession(data)
    msgs = asyncio.run(fetch_messages("http://adapter", account_id=1, session=sess))
    assert msgs == data


def test_login_mocked():
    data = {"ok": True}
    sess = DummySession(data)
    resp = asyncio.run(login("http://adapter", "u", "p", account_id=1, session=sess))
    assert resp == data


def test_auth_header():
    dummy = DummySession({"ok": True})
    with patch.dict(os.environ, {"ADAPTER_AUTH_TOKEN": "tok"}):
        asyncio.run(login_adapter("http://adapter", session=dummy))
    assert dummy.headers == {"Authorization": "Bearer tok"}


def test_fetch_events_schema_mismatch(caplog):
    bad = [{"id": 1, "link": "l"}]
    sess = DummySession(bad)
    with caplog.at_level(logging.WARNING):
        events = asyncio.run(
            fetch_events("http://adapter", "cities/1", account_id=1, session=sess)
        )
    assert events == [{"link": "l"}]
    assert any(r.message == "adapter_schema_mismatch" for r in caplog.records)


def test_close_session():
    dummy = DummySession({"ok": True})
    with patch("bot.adapter_client.ClientSession", return_value=dummy):
        asyncio.run(login_adapter("http://adapter"))
    asyncio.run(close_session())
    assert dummy.closed
