import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bot.db import hash_credentials


def test_hash_credentials_uses_salt(monkeypatch):
    monkeypatch.setenv("CREDENTIAL_SALT", "salt1")
    h1 = hash_credentials("user", "pass")
    monkeypatch.setenv("CREDENTIAL_SALT", "salt2")
    h2 = hash_credentials("user", "pass")
    assert h1 != h2
