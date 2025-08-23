import pytest

from bot import main


def test_adapter_base_url_requires_https(monkeypatch):
    monkeypatch.setenv("DISCORD_TOKEN", "x")
    monkeypatch.setenv("ADAPTER_AUTH_TOKEN", "x")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("ADAPTER_BASE_URL", "http://adapter:8000")
    monkeypatch.delenv("MOCK_ADAPTER", raising=False)
    with pytest.raises(SystemExit) as exc:
        main.main()
    assert "https://" in str(exc.value)
