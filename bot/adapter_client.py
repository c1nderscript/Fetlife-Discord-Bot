from __future__ import annotations

from typing import Any
import json
import os
import logging
from functools import lru_cache
from pathlib import Path

from aiohttp import ClientSession, ClientTimeout
from jsonschema import ValidationError, validate


logger = logging.getLogger(__name__)

SCHEMAS = Path(__file__).resolve().parents[1] / "schemas"

DEFAULT_TIMEOUT = ClientTimeout(total=30)
_session: ClientSession | None = None


def _get_session(session: ClientSession | None = None) -> ClientSession:
    global _session
    if session:
        return session
    if _session is None or _session.closed:
        _session = ClientSession(timeout=DEFAULT_TIMEOUT)
    return _session


@lru_cache
def _load_schema(name: str) -> dict[str, Any]:
    with (SCHEMAS / name).open() as f:
        return json.load(f)


def _validate_list(
    data: list[dict[str, Any]], schema_name: str, fallback_key: str
) -> list[dict[str, Any]]:
    schema = _load_schema(schema_name)
    array_schema = (
        schema if schema.get("type") == "array" else {"type": "array", "items": schema}
    )
    try:
        validate(data, array_schema)
        return data
    except ValidationError:
        logger.warning("adapter_schema_mismatch", extra={"schema": schema_name})
        return [{fallback_key: item.get(fallback_key)} for item in data]


def _headers(extra: dict[str, str] | None = None) -> dict[str, str]:
    headers: dict[str, str] = {}
    token = os.getenv("ADAPTER_AUTH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if extra:
        headers.update(extra)
    return headers


async def login_adapter(base_url: str, session: ClientSession | None = None) -> bool:
    """Log into the adapter using its configured credentials."""
    session = _get_session(session)
    async with session.post(f"{base_url}/login", headers=_headers()) as resp:
        return resp.status == 200


async def login(
    base_url: str,
    username: str,
    password: str,
    account_id: int,
    session: ClientSession | None = None,
) -> dict[str, Any]:
    session = _get_session(session)
    async with session.post(
        f"{base_url}/login",
        json={"username": username, "password": password},
        headers=_headers({"X-Account-ID": str(account_id)}),
    ) as resp:
        resp.raise_for_status()
        return await resp.json()


async def fetch_events(
    base_url: str,
    location: str,
    account_id: int | None = None,
    session: ClientSession | None = None,
) -> list[dict[str, Any]]:
    """Fetch events from the adapter service."""
    extra = {"X-Account-ID": str(account_id)} if account_id is not None else {}
    session = _get_session(session)
    async with session.get(
        f"{base_url}/events", params={"location": location}, headers=_headers(extra)
    ) as resp:
        resp.raise_for_status()
        data = await resp.json()
        return _validate_list(data, "event.json", "link")


async def fetch_writings(
    base_url: str,
    user_id: str,
    account_id: int | None = None,
    session: ClientSession | None = None,
) -> list[dict[str, Any]]:
    """Fetch writings for a user from the adapter service."""
    extra = {"X-Account-ID": str(account_id)} if account_id is not None else {}
    session = _get_session(session)
    async with session.get(
        f"{base_url}/users/{user_id}/writings", headers=_headers(extra)
    ) as resp:
        resp.raise_for_status()
        data = await resp.json()
        return _validate_list(data, "writing.json", "link")


async def fetch_attendees(
    base_url: str,
    event_id: str,
    account_id: int | None = None,
    session: ClientSession | None = None,
) -> list[dict[str, Any]]:
    """Fetch attendees for an event from the adapter service."""
    extra = {"X-Account-ID": str(account_id)} if account_id is not None else {}
    session = _get_session(session)
    async with session.get(
        f"{base_url}/events/{event_id}/attendees", headers=_headers(extra)
    ) as resp:
        resp.raise_for_status()
        data = await resp.json()
        return _validate_list(data, "event_attendees.json", "id")


async def fetch_group_posts(
    base_url: str,
    group_id: str,
    account_id: int | None = None,
    session: ClientSession | None = None,
) -> list[dict[str, Any]]:
    """Fetch posts for a group from the adapter service."""
    extra = {"X-Account-ID": str(account_id)} if account_id is not None else {}
    session = _get_session(session)
    async with session.get(
        f"{base_url}/groups/{group_id}/posts", headers=_headers(extra)
    ) as resp:
        resp.raise_for_status()
        data = await resp.json()
        return _validate_list(data, "group_post.json", "link")


async def fetch_messages(
    base_url: str,
    account_id: int | None = None,
    session: ClientSession | None = None,
) -> list[dict[str, Any]]:
    """Fetch direct messages from the adapter service."""
    extra = {"X-Account-ID": str(account_id)} if account_id is not None else {}
    session = _get_session(session)
    async with session.get(f"{base_url}/messages", headers=_headers(extra)) as resp:
        resp.raise_for_status()
        data = await resp.json()
        return _validate_list(data, "message.json", "id")


async def close_session() -> None:
    global _session
    if _session and not _session.closed:
        await _session.close()
    _session = None
