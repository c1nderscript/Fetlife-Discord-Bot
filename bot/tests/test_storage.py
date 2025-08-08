import os
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bot import storage


def setup_db():
    conn = storage.init_db(":memory:")
    return conn


def test_add_and_list_subscription():
    conn = setup_db()
    sub_id = storage.add_subscription(conn, 1, "events", "target")
    subs = storage.list_subscriptions(conn, 1)
    assert subs == [(sub_id, "events", "target")]


def test_remove_subscription():
    conn = setup_db()
    sub_id = storage.add_subscription(conn, 1, "events", "target")
    storage.remove_subscription(conn, sub_id, 1)
    assert storage.list_subscriptions(conn, 1) == []


def test_channel_settings():
    conn = setup_db()
    storage.set_channel_settings(conn, 1, thread_per_event="on")
    settings = storage.get_channel_settings(conn, 1)
    assert settings["thread_per_event"] == "on"
