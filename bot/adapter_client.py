from __future__ import annotations
from __future__ import annotations

from typing import Any, List

import aiohttp


async def fetch_events(base_url: str, location: str) -> List[Any]:
    """Fetch events from adapter service."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{base_url}/events", params={"location": location}) as resp:
            resp.raise_for_status()
            return await resp.json()


async def fetch_writings(base_url: str, user_id: str) -> list[dict[str, Any]]:
    """Fetch writings for a user from the adapter service."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{base_url}/users/{user_id}/writings") as resp:
            resp.raise_for_status()
            return await resp.json()


async def fetch_group_posts(base_url: str, group_id: str) -> list[dict[str, Any]]:
    """Fetch posts for a group from the adapter service."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{base_url}/groups/{group_id}/posts") as resp:
            resp.raise_for_status()
            return await resp.json()
