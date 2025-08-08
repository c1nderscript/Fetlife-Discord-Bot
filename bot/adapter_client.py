from __future__ import annotations

from typing import Any, List

import aiohttp


async def fetch_events(base_url: str, location: str) -> List[Any]:
    """Fetch events from adapter service."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{base_url}/events", params={"location": location}) as resp:
            resp.raise_for_status()
            return await resp.json()
