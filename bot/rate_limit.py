import asyncio
import time


class TokenBucket:
    """Asynchronous token bucket rate limiter."""

    def __init__(self, capacity: int, refill_rate: float) -> None:
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = float(capacity)
        self.updated = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self, tokens: float = 1) -> None:
        async with self._lock:
            await self._add_new_tokens()
            while self.tokens < tokens:
                await asyncio.sleep((tokens - self.tokens) / self.refill_rate)
                await self._add_new_tokens()
            self.tokens -= tokens

    async def _add_new_tokens(self) -> None:
        now = time.monotonic()
        delta = now - self.updated
        if delta > 0:
            self.tokens = min(self.capacity, self.tokens + delta * self.refill_rate)
            self.updated = now

    def get_tokens(self) -> float:
        return self.tokens
