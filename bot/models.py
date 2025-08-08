from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.sql import func

from .db import Base


class Guild(Base):
    __tablename__ = "guilds"
    id = Column(BigInteger, primary_key=True)
    name = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)


class Channel(Base):
    __tablename__ = "channels"
    id = Column(BigInteger, primary_key=True)
    guild_id = Column(BigInteger, ForeignKey("guilds.id"), nullable=True)
    name = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    settings_json = Column(JSON, nullable=True)


class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    channel_id = Column(BigInteger, ForeignKey("channels.id"), nullable=False)
    type = Column(String, nullable=False)
    target_id = Column(String, nullable=False)
    target_kind = Column(String, nullable=False)
    filters_json = Column(JSON, nullable=True)
    created_by = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    active = Column(Boolean, server_default="1", nullable=False)


class Cursor(Base):
    __tablename__ = "cursors"
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), primary_key=True)
    last_seen_at = Column(DateTime, nullable=True)
    last_item_ids_json = Column(JSON, nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)


class RelayLog(Base):
    __tablename__ = "relay_log"
    id = Column(Integer, primary_key=True, autoincrement=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=False)
    item_id = Column(String, nullable=False)
    item_hash = Column(String, nullable=True)
    relayed_at = Column(DateTime, server_default=func.now(), nullable=False)


class Profile(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nickname = Column(String, nullable=False)
    fl_id = Column(String, unique=True, nullable=False)
    last_seen_at = Column(DateTime, nullable=True)


class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, autoincrement=True)
    fl_id = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    city = Column(String, nullable=True)
    region = Column(String, nullable=True)
    start_at = Column(DateTime, nullable=True)
    permalink = Column(String, nullable=True)
    last_populated_at = Column(DateTime, nullable=True)


class RSVP(Base):
    __tablename__ = "rsvps"
    event_id = Column(Integer, ForeignKey("events.id"), primary_key=True)
    profile_fl_id = Column(String, primary_key=True)
    status = Column(String, nullable=False)
    seen_at = Column(DateTime, server_default=func.now(), nullable=False)
