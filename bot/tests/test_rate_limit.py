import asyncio
import time
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bot.rate_limit import TokenBucket


@pytest.mark.asyncio
async def test_token_bucket_refill():
    bucket = TokenBucket(2, 1)  # 2 tokens, 1 per second refill
    await bucket.acquire()
    await bucket.acquire()
    start = time.perf_counter()
    await bucket.acquire()
    elapsed = time.perf_counter() - start
    assert elapsed >= 1
