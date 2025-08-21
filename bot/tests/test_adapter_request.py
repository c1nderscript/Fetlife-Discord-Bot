import asyncio
import pytest

from bot.main import adapter_request


def test_adapter_request_propagates_cancellation():
    async def slow_fn():
        await asyncio.sleep(1)

    async def run():
        task = asyncio.create_task(adapter_request(slow_fn))
        await asyncio.sleep(0)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    asyncio.run(run())
