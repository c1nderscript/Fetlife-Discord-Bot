import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bot import storage


def setup_db():
    return storage.init_db("sqlite:///:memory:")


def test_cursor_roundtrip():
    db = setup_db()
    sub_id = storage.add_subscription(db, 1, "events", "target")
    last_seen, ids = storage.get_cursor(db, sub_id)
    assert last_seen is None and ids == []
    now = datetime.utcnow()
    storage.update_cursor(db, sub_id, now, ["a", "b"])
    last_seen, ids = storage.get_cursor(db, sub_id)
    assert ids == ["a", "b"]
    assert last_seen == now
