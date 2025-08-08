import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).resolve().parents[2]))

from bot.config import get_channel_config, load_config


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
