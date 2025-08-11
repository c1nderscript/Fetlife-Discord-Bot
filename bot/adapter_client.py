from __future__ import annotations

from typing import Any

import aiohttp


async def login(
    base_url: str, username: str, password: str, account_id: int
) -> dict[str, Any]:
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{base_url}/login",
            json={"username": username, "password": password},
            headers={"X-Account-ID": str(account_id)},
        ) as resp:
            resp.raise_for_status()
            return await resp.json()


async def fetch_events(
    base_url: str, location: str, account_id: int | None = None
) -> list[dict[str, Any]]:
    """Fetch events from the adapter service."""
    headers = {"X-Account-ID": str(account_id)} if account_id is not None else {}
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{base_url}/events", params={"location": location}, headers=headers
        ) as resp:
            resp.raise_for_status()
            return await resp.json()


async def fetch_writings(
    base_url: str, user_id: str, account_id: int | None = None
) -> list[dict[str, Any]]:
    """Fetch writings for a user from the adapter service."""
    headers = {"X-Account-ID": str(account_id)} if account_id is not None else {}
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{base_url}/users/{user_id}/writings", headers=headers
        ) as resp:
            resp.raise_for_status()
            return await resp.json()


async def fetch_attendees(
    base_url: str, event_id: str, account_id: int | None = None
) -> list[dict[str, Any]]:
    """Fetch attendees for an event from the adapter service."""
    headers = {"X-Account-ID": str(account_id)} if account_id is not None else {}
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{base_url}/events/{event_id}/attendees", headers=headers
        ) as resp:
            resp.raise_for_status()
            return await resp.json()


async def fetch_group_posts(
    base_url: str, group_id: str, account_id: int | None = None
) -> list[dict[str, Any]]:
    """Fetch posts for a group from the adapter service."""
    headers = {"X-Account-ID": str(account_id)} if account_id is not None else {}
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{base_url}/groups/{group_id}/posts", headers=headers
        ) as resp:
            resp.raise_for_status()
            return await resp.json()
