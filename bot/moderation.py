from __future__ import annotations

"""Moderation helpers and infractions models."""

from datetime import datetime, timedelta
from enum import Enum
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Session

from .db import Base, SessionLocal


class InfractionType(str, Enum):
    WARN = "warn"
    MUTE = "mute"
    KICK = "kick"
    BAN = "ban"
    TIMEOUT = "timeout"


class Infraction(Base):
    __tablename__ = "infractions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False)
    user_id = Column(BigInteger, nullable=False)
    moderator_id = Column(BigInteger, nullable=False)
    type = Column(String, nullable=False)
    reason = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    expires_at = Column(DateTime, nullable=True)
    appealed = Column(Boolean, server_default="0", nullable=False)
    resolved = Column(Boolean, server_default="0", nullable=False)


class Appeal(Base):
    __tablename__ = "appeals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    infraction_id = Column(Integer, nullable=False)
    user_id = Column(BigInteger, nullable=False)
    text = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    resolved = Column(Boolean, server_default="0", nullable=False)


def add_infraction(
    db: Session,
    guild_id: int,
    user_id: int,
    moderator_id: int,
    inf_type: InfractionType,
    reason: Optional[str] = None,
    expires_at: Optional[datetime] = None,
) -> Infraction:
    """Persist an infraction and return it."""
    infra = Infraction(
        guild_id=guild_id,
        user_id=user_id,
        moderator_id=moderator_id,
        type=inf_type.value,
        reason=reason,
        expires_at=expires_at,
    )
    db.add(infra)
    db.commit()
    db.refresh(infra)
    return infra


def list_infractions(db: Session, guild_id: int, user_id: int) -> list[Infraction]:
    return (
        db.query(Infraction)
        .filter_by(guild_id=guild_id, user_id=user_id)
        .order_by(Infraction.id.desc())
        .all()
    )


def escalate(db: Session, guild_id: int, user_id: int) -> Optional[InfractionType]:
    """Determine next escalation step based on infraction history."""
    warns = (
        db.query(Infraction)
        .filter_by(guild_id=guild_id, user_id=user_id, type=InfractionType.WARN.value)
        .count()
    )
    mutes = (
        db.query(Infraction)
        .filter_by(guild_id=guild_id, user_id=user_id, type=InfractionType.MUTE.value)
        .count()
    )
    kicks = (
        db.query(Infraction)
        .filter_by(guild_id=guild_id, user_id=user_id, type=InfractionType.KICK.value)
        .count()
    )
    if warns >= 3 and mutes == 0:
        return InfractionType.MUTE
    if mutes >= 2 and kicks == 0:
        return InfractionType.KICK
    if kicks >= 2:
        return InfractionType.BAN
    return None


def submit_appeal(db: Session, infraction_id: int, user_id: int, text: str) -> Appeal:
    appeal = Appeal(infraction_id=infraction_id, user_id=user_id, text=text)
    db.add(appeal)
    db.commit()
    db.refresh(appeal)
    return appeal


def register_routes(app, db: Session) -> None:
    """Register simple appeal routes on management web app."""
    from aiohttp import web

    async def appeals_page(request: web.Request) -> web.Response:
        rows = db.query(Appeal).filter_by(resolved=False).all()
        items = "".join(
            f"<li>{a.id} infraction:{a.infraction_id} {a.text}<form method='post' action='/appeals/{a.id}/resolve'><button>Resolve</button></form></li>"
            for a in rows
        )
        return web.Response(
            text=f"<h1>Appeals</h1><ul>{items}</ul>", content_type="text/html"
        )

    async def resolve(request: web.Request) -> web.Response:
        appeal_id = int(request.match_info["app_id"])
        db.query(Appeal).filter(Appeal.id == appeal_id).update({Appeal.resolved: True})
        db.commit()
        raise web.HTTPFound("/appeals")

    app.router.add_get("/appeals", appeals_page)
    app.router.add_post(r"/appeals/{app_id:\d+}/resolve", resolve)
