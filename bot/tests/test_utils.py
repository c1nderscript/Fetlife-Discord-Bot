import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import discord

from bot.utils import (
    format_event_embed,
    matches_filters,
    parse_subscribe_command,
)


def test_parse_subscribe_command():
    sub_type, target, filters = parse_subscribe_command("events location:cities/1 min_attendees:10 keywords:rope,consent")
    assert sub_type == "events"
    assert target == "location:cities/1"
    assert filters == {"min_attendees": 10, "keywords": ["rope", "consent"]}


def test_matches_filters():
    filters = {"keywords": ["rope"], "city": "NYC", "min_attendees": 5}
    item = {"title": "Rope Night", "city": "NYC", "attendees": 10}
    assert matches_filters(item, filters)
    item2 = {"title": "Other", "city": "NYC", "attendees": 10}
    assert not matches_filters(item2, filters)


def test_format_event_embed():
    event = {
        "title": "Party",
        "link": "https://example.com",
        "time": "2024-01-01",
    }
    embed = format_event_embed(event)
    assert isinstance(embed, discord.Embed)
    assert embed.title == "📅 Party"
    assert embed.description == "https://example.com"
    assert embed.fields[0].name == "Time"
    assert embed.fields[0].value == "2024-01-01"
