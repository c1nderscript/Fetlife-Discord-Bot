from __future__ import annotations

import asyncio
import logging
from io import BytesIO
from typing import Dict, Optional

import discord
from telethon import TelegramClient, events  # type: ignore[import-untyped]

from .config import load_config, save_config

logger = logging.getLogger("flbot")


class TelegramBridge:
    def __init__(
        self,
        bot,
        api_id: Optional[int] = None,
        api_hash: Optional[str] = None,
        *,
        config: Optional[Dict] = None,
        config_path: str = "config.yaml",
        client: Optional[TelegramClient] = None,
    ) -> None:
        self.bot = bot
        self.config_path = config_path
        self.client = client or TelegramClient("tg_bridge", api_id, api_hash)
        if config is None:
            config = load_config(config_path)
        self.config = config
        self.mappings: Dict[str, str] = config.get("telegram_bridge", {}).get(
            "mappings", {}
        )

    async def start(self) -> None:
        self.client.add_event_handler(self._handle_message, events.NewMessage)
        while True:
            try:
                await self.client.start()
                break
            except Exception as exc:  # pragma: no cover - network errors
                logger.exception("telegram start failed: %s", exc)
                await asyncio.sleep(5)

    async def stop(self) -> None:
        await self.client.disconnect()

    async def _handle_message(self, event) -> None:
        chat_id = str(event.chat_id)
        channel_id = self.mappings.get(chat_id)
        if not channel_id:
            return
        channel = self.bot.get_channel(int(channel_id))
        if channel:
            text = getattr(event, "raw_text", "")
            files = []
            if getattr(event, "photo", None) or getattr(event, "document", None):
                try:
                    buf = BytesIO()
                    await event.download_media(file=buf)
                    buf.seek(0)
                    filename = (
                        getattr(getattr(event, "file", None), "name", None)
                        or "attachment"
                    )
                    files = [discord.File(buf, filename)]
                except Exception as exc:  # pragma: no cover - simple error path
                    logger.exception("telegram media download failed: %s", exc)
            try:
                await channel.send(text if text else None, files=files or None)
            except Exception as exc:  # pragma: no cover - simple error path
                logger.exception("telegram relay failed: %s", exc)

    def add_mapping(self, chat_id: int, channel_id: int) -> None:
        self.mappings[str(chat_id)] = str(channel_id)
        self._persist()

    def remove_mapping(self, chat_id: int) -> None:
        self.mappings.pop(str(chat_id), None)
        self._persist()

    def _persist(self) -> None:
        cfg = load_config(self.config_path)
        bridge_cfg = cfg.setdefault("telegram_bridge", {})
        bridge_cfg["mappings"] = self.mappings
        save_config(cfg, self.config_path)

    async def send_to_telegram(self, channel_id: int, text: str) -> None:
        for chat_id, mapped in self.mappings.items():
            if mapped == str(channel_id):
                try:
                    await self.client.send_message(int(chat_id), text)
                except Exception as exc:  # pragma: no cover - simple error path
                    logger.exception("telegram send failed: %s", exc)
