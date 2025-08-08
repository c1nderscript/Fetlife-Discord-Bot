import json
import sqlite3
from typing import Any, Dict, Iterable, Tuple

DB_PATH = "bot.db"


def init_db(path: str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            target TEXT NOT NULL,
            filters TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS channel_settings (
            channel_id INTEGER PRIMARY KEY,
            settings TEXT
        )
        """
    )
    conn.commit()
    return conn


def add_subscription(
    conn: sqlite3.Connection,
    channel_id: int,
    sub_type: str,
    target: str,
    filters: Dict[str, Any] | None = None,
) -> int:
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO subscriptions(channel_id, type, target, filters) VALUES(?, ?, ?, ?)",
        (channel_id, sub_type, target, json.dumps(filters or {})),
    )
    conn.commit()
    return cur.lastrowid


def list_subscriptions(conn: sqlite3.Connection, channel_id: int) -> Iterable[Tuple[int, str, str]]:
    cur = conn.cursor()
    cur.execute(
        "SELECT id, type, target FROM subscriptions WHERE channel_id = ? ORDER BY id",
        (channel_id,),
    )
    return cur.fetchall()


def remove_subscription(conn: sqlite3.Connection, sub_id: int, channel_id: int) -> None:
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM subscriptions WHERE id = ? AND channel_id = ?",
        (sub_id, channel_id),
    )
    conn.commit()


def set_channel_settings(conn: sqlite3.Connection, channel_id: int, **settings: Any) -> None:
    cur = conn.cursor()
    cur.execute(
        "REPLACE INTO channel_settings(channel_id, settings) VALUES(?, ?)",
        (channel_id, json.dumps(settings)),
    )
    conn.commit()


def get_channel_settings(conn: sqlite3.Connection, channel_id: int) -> Dict[str, Any]:
    cur = conn.cursor()
    cur.execute("SELECT settings FROM channel_settings WHERE channel_id = ?", (channel_id,))
    row = cur.fetchone()
    return json.loads(row[0]) if row else {}
