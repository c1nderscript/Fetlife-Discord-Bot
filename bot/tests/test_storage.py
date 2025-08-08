from pathlib import Path

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bot import storage


def setup_db():
    db = storage.init_db("sqlite:///:memory:")
    return db


def test_add_and_list_subscription():
    db = setup_db()
    sub_id = storage.add_subscription(db, 1, "events", "target")
    subs = storage.list_subscriptions(db, 1)
    assert subs == [(sub_id, "events", "target")]


def test_remove_subscription():
    db = setup_db()
    sub_id = storage.add_subscription(db, 1, "events", "target")
    storage.remove_subscription(db, sub_id, 1)
    assert storage.list_subscriptions(db, 1) == []


def test_channel_settings():
    db = setup_db()
    storage.set_channel_settings(db, 1, thread_per_event="on")
    settings = storage.get_channel_settings(db, 1)
    assert settings["thread_per_event"] == "on"
