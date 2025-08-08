from __future__ import annotations

from typing import Any, Dict, Iterable, Tuple

from sqlalchemy.orm import Session

from .db import init_db as _init_db
from . import models


def init_db(url: str | None = None) -> Session:
    return _init_db(url)


def add_subscription(
    db: Session,
    channel_id: int,
    sub_type: str,
    target: str,
    filters: Dict[str, Any] | None = None,
) -> int:
    if ":" in target:
        target_kind, target_id = target.split(":", 1)
    else:
        target_kind, target_id = "raw", target
    channel = db.get(models.Channel, channel_id)
    if not channel:
        channel = models.Channel(id=channel_id)
        db.add(channel)
    sub = models.Subscription(
        channel_id=channel_id,
        type=sub_type,
        target_id=target_id,
        target_kind=target_kind,
        filters_json=filters or {},
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub.id


def list_subscriptions(db: Session, channel_id: int) -> Iterable[Tuple[int, str, str]]:
    subs = (
        db.query(models.Subscription.id, models.Subscription.type, models.Subscription.target_id)
        .filter(models.Subscription.channel_id == channel_id)
        .order_by(models.Subscription.id)
        .all()
    )
    return subs


def remove_subscription(db: Session, sub_id: int, channel_id: int) -> None:
    db.query(models.Subscription).filter(
        models.Subscription.id == sub_id, models.Subscription.channel_id == channel_id
    ).delete()
    db.commit()


def set_channel_settings(db: Session, channel_id: int, **settings: Any) -> None:
    channel = db.get(models.Channel, channel_id)
    if not channel:
        channel = models.Channel(id=channel_id, settings_json=settings)
        db.add(channel)
    else:
        current = channel.settings_json or {}
        current.update(settings)
        channel.settings_json = current
    db.commit()


def get_channel_settings(db: Session, channel_id: int) -> Dict[str, Any]:
    channel = db.get(models.Channel, channel_id)
    return channel.settings_json or {} if channel else {}


def get_cursor(db: Session, sub_id: int) -> Tuple[Any | None, list[str]]:
    cur = db.get(models.Cursor, sub_id)
    if not cur:
        return None, []
    ids = cur.last_item_ids_json or []
    return cur.last_seen_at, ids


def update_cursor(
    db: Session, sub_id: int, last_seen_at: Any, last_item_ids: list[str]
) -> None:
    cur = db.get(models.Cursor, sub_id)
    if not cur:
        cur = models.Cursor(subscription_id=sub_id)
        db.add(cur)
    cur.last_seen_at = last_seen_at
    cur.last_item_ids_json = last_item_ids
    db.commit()


def has_relayed(db: Session, sub_id: int, item_id: str) -> bool:
    return (
        db.query(models.RelayLog)
        .filter(models.RelayLog.subscription_id == sub_id, models.RelayLog.item_id == item_id)
        .first()
        is not None
    )


def record_relay(db: Session, sub_id: int, item_id: str, item_hash: str | None = None) -> None:
    db.add(models.RelayLog(subscription_id=sub_id, item_id=item_id, item_hash=item_hash))
    db.commit()
