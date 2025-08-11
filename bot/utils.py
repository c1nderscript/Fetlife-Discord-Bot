from __future__ import annotations

from typing import Any, Dict, List, Tuple

import discord


def parse_subscribe_command(text: str) -> Tuple[str, str, Dict[str, Any]]:
    """Parse a simplified subscribe command string.

    Example: "events location:cities/5898 radius_km:50 keywords:rope,consent"
    """
    parts = text.strip().split()
    if len(parts) < 2:
        raise ValueError("command requires type and target")
    sub_type = parts[0]
    target = parts[1]
    filters: Dict[str, Any] = {}
    for part in parts[2:]:
        if ":" not in part:
            continue
        key, value = part.split(":", 1)
        if key == "keywords":
            filters[key] = [v.strip() for v in value.split(",") if v.strip()]
        elif value.isdigit():
            filters[key] = int(value)
        else:
            filters[key] = value
    return sub_type, target, filters


def matches_filters(item: Dict[str, Any], filters: Dict[str, Any]) -> bool:
    """Return True if *item* satisfies *filters*.

    Supported filters: keywords (list), city (str), min_attendees (int).
    """
    keywords: List[str] = filters.get("keywords", [])
    if keywords:
        haystack = " ".join(str(v) for v in item.values()).lower()
        if not any(k.lower() in haystack for k in keywords):
            return False
    city = filters.get("city")
    if city and item.get("city", "").lower() != str(city).lower():
        return False
    min_attendees = filters.get("min_attendees")
    if isinstance(min_attendees, int) and int(item.get("attendees", 0)) < min_attendees:
        return False
    return True


def format_event_embed(event: Dict[str, Any]) -> discord.Embed:
    """Return a Discord embed for *event*."""
    title = f"\U0001f4c5 {event.get('title', '')}"
    description = event.get("link", "")
    embed = discord.Embed(title=title, description=description)
    if "time" in event:
        embed.add_field(name="Time", value=str(event["time"]))
    return embed
