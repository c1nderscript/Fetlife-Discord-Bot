from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml


def load_config(path: str = "config.yaml") -> Dict[str, Any]:
    cfg_path = Path(path)
    if not cfg_path.exists():
        alt = Path(__file__).resolve().parent.parent / path
        if alt.exists():
            cfg_path = alt
        else:
            return {}
    with cfg_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data


def save_config(config: Dict[str, Any], path: str = "config.yaml") -> None:
    cfg_path = Path(path)
    if not cfg_path.exists():
        cfg_path = Path(__file__).resolve().parent.parent / path
    with cfg_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(config, f)


def get_channel_config(config: Dict[str, Any], guild_id: int | None, channel_id: int) -> Dict[str, Any]:
    settings: Dict[str, Any] = {}
    if not config:
        return settings
    settings.update(config.get("defaults", {}))
    if guild_id is None:
        return settings
    guild_cfg = config.get("guilds", {}).get(str(guild_id), {})
    # guild-level settings except channels
    for key, value in guild_cfg.items():
        if key != "channels":
            settings[key] = value
    channel_cfg = guild_cfg.get("channels", {}).get(str(channel_id), {})
    settings.update(channel_cfg)
    return settings
