import time
from typing import Tuple, Optional
from app.core.cache import cache


class RateLimiter:
    def __init__(self, key_prefix: str = "rate_limit"):
        self.key_prefix = key_prefix

    async def check(self, key: str, limit: int, period: int) -> Tuple[bool, int]:
        """
        Check if request is allowed.
        Returns (allowed, remaining) where remaining is number of requests left in current window.
        """
        now = int(time.time())
        window_key = f"{self.key_prefix}:{key}:{now // period}"
        # Use Redis INCR and expire
        count = await cache.client.incr(window_key)
        if count == 1:
            await cache.client.expire(window_key, period)
        remaining = max(0, limit - count)
        if count > limit:
            return False, remaining
        return True, remaining
