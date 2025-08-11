import asyncio
from unittest.mock import AsyncMock, patch

from bot import main


def test_fl_login_success():
    interaction = AsyncMock()
    interaction.response.send_message = AsyncMock()
    with patch("bot.main.adapter_client.login_adapter", AsyncMock(return_value=True)), \
         patch("bot.main.bot_bucket.acquire", AsyncMock()), \
         patch("bot.main.bot_tokens.set"):
        asyncio.run(main.fl_login(interaction))
    interaction.response.send_message.assert_called_once_with("Adapter login successful")


def test_fl_login_failure():
    interaction = AsyncMock()
    interaction.response.send_message = AsyncMock()
    with patch("bot.main.adapter_client.login_adapter", AsyncMock(return_value=False)), \
         patch("bot.main.bot_bucket.acquire", AsyncMock()), \
         patch("bot.main.bot_tokens.set"):
        asyncio.run(main.fl_login(interaction))
    interaction.response.send_message.assert_called_once_with("Adapter login failed")
