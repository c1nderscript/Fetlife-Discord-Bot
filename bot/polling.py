from __future__ import annotations

import asyncio
from datetime import datetime
from typing import List, Dict

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    BigInteger,
    ForeignKey,
    JSON,
    func,
)
from sqlalchemy.orm import Session

import logging

from .db import Base, SessionLocal
from .utils import get_correlation_id


logger = logging.getLogger(__name__)


class Poll(Base):
    __tablename__ = "polls"

    id = Column(Integer, primary_key=True, autoincrement=True)
    question = Column(String, nullable=False)
    type = Column(String, nullable=False)
    options_json = Column(JSON, nullable=True)
    created_by = Column(BigInteger, nullable=False)
    channel_id = Column(BigInteger, nullable=False)
    message_id = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    closes_at = Column(DateTime, nullable=True)
    closed = Column(Boolean, server_default="0", nullable=False)


class PollVote(Base):
    __tablename__ = "poll_votes"

    poll_id = Column(Integer, ForeignKey("polls.id"), primary_key=True)
    user_id = Column(BigInteger, primary_key=True)
    choice = Column(Integer, nullable=True)
    ranking_json = Column(JSON, nullable=True)
    voted_at = Column(DateTime, server_default=func.now(), nullable=False)


def create_poll(
    db: Session,
    question: str,
    poll_type: str,
    options: List[str],
    created_by: int,
    channel_id: int,
    closes_at: datetime | None = None,
) -> Poll:
    poll = Poll(
        question=question,
        type=poll_type,
        options_json=options,
        created_by=created_by,
        channel_id=channel_id,
        closes_at=closes_at,
    )
    db.add(poll)
    db.commit()
    db.refresh(poll)
    logger.info(
        "poll_created",
        extra={"poll_id": poll.id, "correlation_id": get_correlation_id()},
    )
    return poll


def set_message(db: Session, poll_id: int, message_id: int) -> None:
    poll = db.get(Poll, poll_id)
    if poll:
        poll.message_id = message_id
        db.commit()


def record_vote(
    db: Session,
    poll_id: int,
    user_id: int,
    choice: int | None,
    ranking: List[int] | None = None,
) -> None:
    vote = db.get(PollVote, {"poll_id": poll_id, "user_id": user_id})
    if not vote:
        vote = PollVote(poll_id=poll_id, user_id=user_id)
        db.add(vote)
    vote.choice = choice
    vote.ranking_json = ranking
    db.commit()
    logger.info(
        "poll_vote",
        extra={
            "poll_id": poll_id,
            "user_id": user_id,
            "correlation_id": get_correlation_id(),
        },
    )


def close_poll(db: Session, poll_id: int) -> None:
    poll = db.get(Poll, poll_id)
    if poll and not poll.closed:
        poll.closed = True
        db.commit()
        logger.info(
            "poll_closed",
            extra={"poll_id": poll_id, "correlation_id": get_correlation_id()},
        )


def list_polls(db: Session, active_only: bool = True) -> List[Poll]:
    q = db.query(Poll)
    if active_only:
        q = q.filter_by(closed=False)
    return q.order_by(Poll.id.desc()).all()


def poll_results(db: Session, poll_id: int) -> Dict[str, int]:
    poll = db.get(Poll, poll_id)
    if not poll:
        return {}
    options = poll.options_json or []
    counts = {i: 0 for i in range(len(options))}
    for vote in db.query(PollVote).filter_by(poll_id=poll_id).all():
        if vote.choice is not None and vote.choice in counts:
            counts[vote.choice] += 1
    return {options[i]: counts[i] for i in counts}


def schedule_close(bot, poll_id: int, closes_at: datetime) -> None:
    delay = (closes_at - datetime.utcnow()).total_seconds()
    if delay <= 0:
        return

    async def _close_later():
        await asyncio.sleep(delay)
        db = SessionLocal()
        try:
            poll = db.get(Poll, poll_id)
            if not poll or poll.closed:
                return
            close_poll(db, poll_id)
        finally:
            db.close()
        channel = bot.get_channel(poll.channel_id) if poll else None
        if hasattr(channel, "fetch_message") and poll and poll.message_id:
            try:
                msg = await channel.fetch_message(poll.message_id)
                await msg.edit(view=None)
            except Exception:
                pass

    bot.loop.create_task(_close_later())
