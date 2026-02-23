"""
Per-user and per-project rate limiting using an in-process sliding window.

For production, replace the in-memory store with a Redis backend by
implementing a Redis-backed version of SlidingWindowRateLimiter.
"""
from __future__ import annotations

import logging
import time
from collections import defaultdict, deque
from threading import Lock
from typing import Optional

from fastapi import HTTPException, Request, status

logger = logging.getLogger(__name__)


class SlidingWindowRateLimiter:
    """
    Thread-safe sliding window rate limiter backed by an in-process deque.

    Args:
        max_calls: Maximum number of calls allowed in the window.
        window_seconds: Length of the sliding window in seconds.
        name: Human-readable name for logging.
    """

    def __init__(self, max_calls: int, window_seconds: int, name: str = "default") -> None:
        self.max_calls = max_calls
        self.window_seconds = window_seconds
        self.name = name
        self._buckets: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def is_allowed(self, key: str) -> tuple[bool, int]:
        """
        Check whether ``key`` is within the rate limit.

        Returns:
            (allowed, remaining): allowed is True if the call should proceed;
            remaining is the number of calls left in this window.
        """
        now = time.monotonic()
        cutoff = now - self.window_seconds

        with self._lock:
            bucket = self._buckets[key]
            # Evict timestamps outside the window
            while bucket and bucket[0] < cutoff:
                bucket.popleft()

            if len(bucket) >= self.max_calls:
                return False, 0

            bucket.append(now)
            return True, self.max_calls - len(bucket)

    def check(self, key: str, *, correlation_id: Optional[str] = None) -> None:
        """
        Like :meth:`is_allowed` but raises HTTP 429 on limit exceeded.

        Args:
            key: Unique identifier (e.g. user_id or project_id).
            correlation_id: Request ID for audit logging.
        """
        allowed, remaining = self.is_allowed(key)
        if not allowed:
            logger.warning(
                "Rate limit exceeded for key=%s limiter=%s correlation_id=%s",
                key,
                self.name,
                correlation_id,
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded ({self.max_calls} req/{self.window_seconds}s).",
                headers={"Retry-After": str(self.window_seconds)},
            )


# ---------------------------------------------------------------------------
# Pre-built limiters
# ---------------------------------------------------------------------------

# 60 API calls per user per minute
user_api_limiter = SlidingWindowRateLimiter(
    max_calls=60,
    window_seconds=60,
    name="user_api",
)

# 10 project start operations per user per hour
project_start_limiter = SlidingWindowRateLimiter(
    max_calls=10,
    window_seconds=3600,
    name="project_start",
)

# 5 login attempts per IP per 15 minutes  (brute-force protection)
login_limiter = SlidingWindowRateLimiter(
    max_calls=5,
    window_seconds=900,
    name="login",
)
