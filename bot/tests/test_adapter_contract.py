import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from jsonschema import validate

FIXTURES = Path(__file__).parent / "fixtures"
SCHEMAS = Path(__file__).resolve().parents[2] / "schemas"


def load(name: str, base: Path) -> dict:
    with (base / name).open("r", encoding="utf-8") as f:
        return json.load(f)


def test_event_contract():
    data = load("event.json", FIXTURES)
    schema = load("event.json", SCHEMAS)
    validate(instance=data, schema=schema)


def test_writing_contract():
    data = load("writing.json", FIXTURES)
    schema = load("writing.json", SCHEMAS)
    validate(instance=data, schema=schema)


def test_group_post_contract():
    data = load("group_post.json", FIXTURES)
    schema = load("group_post.json", SCHEMAS)
    validate(instance=data, schema=schema)


def test_event_attendees_contract():
    data = load("event_attendees.json", FIXTURES)
    schema = load("event_attendees.json", SCHEMAS)
    validate(instance=data, schema=schema)


def test_message_contract():
    data = load("message.json", FIXTURES)
    schema = load("message.json", SCHEMAS)
    validate(instance=data, schema=schema)
