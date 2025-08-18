import pathlib
import sys

import pytest

sys.path.append(str(pathlib.Path(__file__).resolve().parents[2]))

from bot.config import get_channel_config, get_guild_config, load_config
from bot import main


def test_load_config(tmp_path):
    cfg_file = tmp_path / "config.yaml"
    cfg_file.write_text("defaults:\n  foo: bar\n")
    cfg = load_config(str(cfg_file))
    assert cfg["defaults"]["foo"] == "bar"


def test_get_channel_config():
    cfg = {
        "defaults": {"a": 1},
        "guilds": {
            "1": {
                "b": 2,
                "channels": {"10": {"c": 3}},
            }
        },
    }
    result = get_channel_config(cfg, 1, 10)
    assert result == {"a": 1, "b": 2, "c": 3}


def test_get_guild_config():
    cfg = {
        "defaults": {"a": 1},
        "guilds": {"1": {"b": 2, "channels": {"10": {"c": 3}}}},
    }
    result = get_guild_config(cfg, 1)
    assert result == {"a": 1, "b": 2}


def test_missing_discord_token(monkeypatch):
    monkeypatch.delenv("DISCORD_TOKEN", raising=False)
    monkeypatch.setenv("ADAPTER_AUTH_TOKEN", "x")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    with pytest.raises(SystemExit) as exc:
        main.main()
    assert "DISCORD_TOKEN" in str(exc.value)


def test_missing_adapter_auth_token(monkeypatch):
    monkeypatch.setenv("DISCORD_TOKEN", "x")
    monkeypatch.delenv("ADAPTER_AUTH_TOKEN", raising=False)
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    with pytest.raises(SystemExit) as exc:
        main.main()
    assert "ADAPTER_AUTH_TOKEN" in str(exc.value)


def test_missing_database_settings(monkeypatch):
    monkeypatch.setenv("DISCORD_TOKEN", "x")
    monkeypatch.setenv("ADAPTER_AUTH_TOKEN", "x")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("DB_HOST", raising=False)
    monkeypatch.delenv("DB_NAME", raising=False)
    with pytest.raises(SystemExit) as exc:
        main.main()
    assert "database settings" in str(exc.value)
