from __future__ import annotations

# mypy: ignore-errors

from typing import Any, Dict, Iterable, Tuple

from sqlalchemy.orm import Session

from .db import init_db as _init_db, hash_credentials
from . import models


def init_db(url: str | None = None) -> Session:
    return _init_db(url)


def add_subscription(
    db: Session,
    channel_id: int,
    sub_type: str,
    target: str,
    filters: Dict[str, Any] | None = None,
    account_id: int | None = None,
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
        account_id=account_id,
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub.id


def add_account(db: Session, username: str, password: str) -> int:
    cred_hash = hash_credentials(username, password)
    acct = models.Account(username=username, credential_hash=cred_hash)
    db.add(acct)
    db.commit()
    db.refresh(acct)
    return acct.id


def list_accounts(db: Session) -> Iterable[Tuple[int, str]]:
    return (
        db.query(models.Account.id, models.Account.username)
        .order_by(models.Account.id)
        .all()
    )


def remove_account(db: Session, account_id: int) -> None:
    db.query(models.Account).filter(models.Account.id == account_id).delete()
    db.commit()


def list_subscriptions(
    db: Session, channel_id: int
) -> Iterable[Tuple[int, str, str, int | None]]:
    subs = (
        db.query(
            models.Subscription.id,
            models.Subscription.type,
            models.Subscription.target_id,
            models.Subscription.account_id,
        )
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
        .filter(
            models.RelayLog.subscription_id == sub_id,
            models.RelayLog.item_id == item_id,
        )
        .first()
        is not None
    )


def record_relay(
    db: Session, sub_id: int, item_id: str, item_hash: str | None = None
) -> None:
    db.add(
        models.RelayLog(subscription_id=sub_id, item_id=item_id, item_hash=item_hash)
    )
    db.commit()


def upsert_profile(
    db: Session,
    fl_id: str,
    nickname: str,
    last_seen_at: Any | None = None,
) -> int:
    profile = db.query(models.Profile).filter(models.Profile.fl_id == fl_id).first()
    if profile:
        profile.nickname = nickname
        if last_seen_at is not None:
            profile.last_seen_at = last_seen_at
    else:
        profile = models.Profile(
            fl_id=fl_id, nickname=nickname, last_seen_at=last_seen_at
        )
        db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile.id


def upsert_event(
    db: Session,
    fl_id: str,
    title: str,
    city: str | None = None,
    region: str | None = None,
    start_at: Any | None = None,
    permalink: str | None = None,
    last_populated_at: Any | None = None,
) -> int:
    event = db.query(models.Event).filter(models.Event.fl_id == fl_id).first()
    if event:
        event.title = title
        event.city = city
        event.region = region
        event.start_at = start_at
        event.permalink = permalink
        event.last_populated_at = last_populated_at
    else:
        event = models.Event(
            fl_id=fl_id,
            title=title,
            city=city,
            region=region,
            start_at=start_at,
            permalink=permalink,
            last_populated_at=last_populated_at,
        )
        db.add(event)
    db.commit()
    db.refresh(event)
    return event.id


def upsert_rsvp(
    db: Session,
    event_fl_id: str,
    profile_fl_id: str,
    status: str,
    seen_at: Any | None = None,
) -> None:
    event = db.query(models.Event).filter(models.Event.fl_id == event_fl_id).first()
    if not event:
        event = models.Event(fl_id=event_fl_id, title="")
        db.add(event)
        db.flush()
    rsvp = (
        db.query(models.RSVP)
        .filter(
            models.RSVP.event_id == event.id,
            models.RSVP.profile_fl_id == profile_fl_id,
        )
        .first()
    )
    if rsvp:
        rsvp.status = status
        if seen_at is not None:
            rsvp.seen_at = seen_at
    else:
        rsvp = models.RSVP(
            event_id=event.id,
            profile_fl_id=profile_fl_id,
            status=status,
            seen_at=seen_at,
        )
        db.add(rsvp)
    db.commit()
