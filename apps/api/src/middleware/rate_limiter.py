"""
Advanced Rate Limiter

Redis-based rate limiting with sliding window algorithm.
Supports per-client tracking, burst allowances, and whitelisting.
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any, Literal
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, Field
import logging
import time
import hashlib
import json

logger = logging.getLogger(__name__)


class RateLimitConfig(BaseModel):
    """Rate limit configuration"""
    requests_per_minute: int = Field(default=60, ge=0)
    requests_per_hour: int = Field(default=1000, ge=0)
    requests_per_day: int = Field(default=10000, ge=0)
    burst: int = Field(default=10, ge=0, description="Burst allowance")
    whitelist: list[str] = Field(default_factory=list, description="Whitelisted clients")


class RateLimitInfo(BaseModel):
    """Rate limit tracking information"""
    client_id: str
    window_start: float
    request_count: int
    last_request: float
    burst_tokens: int


class RedisRateLimiter:
    """Redis-based rate limiter with sliding window"""

    def __init__(self, redis_client=None):
        """
        Initialize rate limiter

        Args:
            redis_client: Redis client (optional, falls back to in-memory)
        """
        self.redis = redis_client
        self._memory_store: Dict[str, Dict[str, Any]] = {}
        self._use_redis = redis_client is not None

        if not self._use_redis:
            logger.warning("Redis not available, using in-memory rate limiting (not suitable for production)")

    def _get_key(self, client_id: str, window: str) -> str:
        """Generate Redis key for rate limit tracking"""
        return f"ratelimit:{window}:{client_id}"

    async def _redis_get(self, key: str) -> Optional[str]:
        """Get value from Redis"""
        if self._use_redis:
            try:
                value = await self.redis.get(key)
                return value.decode('utf-8') if value else None
            except Exception as e:
                logger.error(f"Redis GET error: {e}")
        return self._memory_store.get(key)

    async def _redis_set(self, key: str, value: str, expire: int):
        """Set value in Redis with expiration"""
        if self._use_redis:
            try:
                await self.redis.setex(key, expire, value)
                return
            except Exception as e:
                logger.error(f"Redis SET error: {e}")
        self._memory_store[key] = value

    async def _redis_incr(self, key: str) -> int:
        """Increment counter in Redis"""
        if self._use_redis:
            try:
                return await self.redis.incr(key)
            except Exception as e:
                logger.error(f"Redis INCR error: {e}")

        # Fallback to memory
        current = int(self._memory_store.get(key, 0))
        current += 1
        self._memory_store[key] = str(current)
        return current

    async def _redis_expire(self, key: str, seconds: int):
        """Set expiration on key"""
        if self._use_redis:
            try:
                await self.redis.expire(key, seconds)
            except Exception as e:
                logger.error(f"Redis EXPIRE error: {e}")

    async def check_rate_limit(
        self,
        client_id: str,
        config: RateLimitConfig,
        window: Literal["minute", "hour", "day"] = "minute"
    ) -> tuple[bool, Dict[str, Any]]:
        """
        Check if client is within rate limit

        Args:
            client_id: Client identifier
            config: Rate limit configuration
            window: Time window (minute/hour/day)

        Returns:
            (allowed, info) tuple with rate limit info
        """
        # Check whitelist
        if client_id in config.whitelist:
            return True, {
                "allowed": True,
                "limit": -1,
                "remaining": -1,
                "reset": None,
                "whitelisted": True
            }

        # Get window parameters
        if window == "minute":
            limit = config.requests_per_minute
            window_seconds = 60
        elif window == "hour":
            limit = config.requests_per_hour
            window_seconds = 3600
        else:  # day
            limit = config.requests_per_day
            window_seconds = 86400

        if limit <= 0:
            # Rate limiting disabled for this window
            return True, {
                "allowed": True,
                "limit": 0,
                "remaining": 0,
                "reset": None,
                "disabled": True
            }

        # Get current timestamp
        now = time.time()
        current_window = int(now / window_seconds)

        # Get rate limit key
        key = self._get_key(client_id, f"{window}:{current_window}")

        # Get current count
        count_str = await self._redis_get(key)
        current_count = int(count_str) if count_str else 0

        # Check burst tokens
        burst_key = self._get_key(client_id, f"burst:{window}")
        burst_tokens_str = await self._redis_get(burst_key)
        burst_tokens = int(burst_tokens_str) if burst_tokens_str else config.burst

        # Calculate remaining
        effective_limit = limit + burst_tokens
        remaining = max(0, effective_limit - current_count)

        # Calculate reset time
        reset_time = (current_window + 1) * window_seconds
        reset_datetime = datetime.fromtimestamp(reset_time, tz=timezone.utc)

        if current_count >= effective_limit:
            # Rate limit exceeded
            logger.warning(
                f"Rate limit exceeded - Client: {client_id}, "
                f"Window: {window}, Count: {current_count}, Limit: {effective_limit}"
            )
            return False, {
                "allowed": False,
                "limit": limit,
                "remaining": 0,
                "reset": reset_datetime.isoformat(),
                "retry_after": int(reset_time - now),
                "burst_used": max(0, current_count - limit)
            }

        # Increment counter
        new_count = await self._redis_incr(key)

        # Set expiration if first request in window
        if new_count == 1:
            await self._redis_expire(key, window_seconds * 2)  # 2x window for safety

        # Update burst tokens
        if new_count > limit and burst_tokens > 0:
            # Using burst capacity
            burst_tokens -= 1
            await self._redis_set(burst_key, str(burst_tokens), window_seconds)

        logger.debug(
            f"Rate limit check - Client: {client_id}, "
            f"Window: {window}, Count: {new_count}/{effective_limit}"
        )

        return True, {
            "allowed": True,
            "limit": limit,
            "remaining": max(0, effective_limit - new_count),
            "reset": reset_datetime.isoformat(),
            "burst_available": burst_tokens
        }

    async def check_all_windows(
        self,
        client_id: str,
        config: RateLimitConfig
    ) -> tuple[bool, Dict[str, Any]]:
        """
        Check all rate limit windows (minute, hour, day)

        Returns:
            (allowed, info) tuple with combined rate limit info
        """
        # Check minute window
        minute_allowed, minute_info = await self.check_rate_limit(
            client_id, config, "minute"
        )

        if not minute_allowed:
            return False, {
                "window": "minute",
                **minute_info
            }

        # Check hour window
        hour_allowed, hour_info = await self.check_rate_limit(
            client_id, config, "hour"
        )

        if not hour_allowed:
            return False, {
                "window": "hour",
                **hour_info
            }

        # Check day window
        day_allowed, day_info = await self.check_rate_limit(
            client_id, config, "day"
        )

        if not day_allowed:
            return False, {
                "window": "day",
                **day_info
            }

        # All windows passed
        return True, {
            "minute": minute_info,
            "hour": hour_info,
            "day": day_info
        }

    async def reset_client_limits(self, client_id: str):
        """Reset all rate limits for a client"""
        patterns = [
            f"ratelimit:minute:*:{client_id}",
            f"ratelimit:hour:*:{client_id}",
            f"ratelimit:day:*:{client_id}",
            f"ratelimit:burst:*:{client_id}"
        ]

        if self._use_redis:
            try:
                for pattern in patterns:
                    keys = await self.redis.keys(pattern)
                    if keys:
                        await self.redis.delete(*keys)
                logger.info(f"Reset rate limits for client: {client_id}")
            except Exception as e:
                logger.error(f"Failed to reset rate limits: {e}")
        else:
            # Memory store
            keys_to_delete = [
                k for k in self._memory_store.keys()
                if client_id in k
            ]
            for key in keys_to_delete:
                del self._memory_store[key]
            logger.info(f"Reset rate limits for client: {client_id}")


class RateLimitMiddleware:
    """FastAPI middleware for rate limiting"""

    def __init__(self, redis_client=None, default_config: Optional[RateLimitConfig] = None):
        """
        Initialize rate limit middleware

        Args:
            redis_client: Redis client (optional)
            default_config: Default rate limit configuration
        """
        self.limiter = RedisRateLimiter(redis_client)
        self.default_config = default_config or RateLimitConfig()

    def extract_client_id(self, request: Request) -> str:
        """Extract client ID from request"""
        # Try header first
        client_id = request.headers.get("X-AIIndex-Client-ID")
        if client_id:
            return client_id.strip()

        # Fall back to IP address
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        # Use client host
        if request.client:
            return request.client.host

        return "unknown"

    async def __call__(self, request: Request, call_next):
        """Process request with rate limiting"""
        # Skip rate limiting for certain endpoints
        skip_paths = ["/health", "/docs", "/redoc", "/openapi.json"]
        if any(request.url.path.startswith(path) for path in skip_paths):
            return await call_next(request)

        # Extract client ID
        client_id = self.extract_client_id(request)

        # Check rate limits
        allowed, info = await self.limiter.check_all_windows(
            client_id,
            self.default_config
        )

        if not allowed:
            # Rate limit exceeded
            logger.warning(f"Rate limit exceeded for client: {client_id}")

            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Too Many Requests",
                    "message": f"Rate limit exceeded for {info['window']} window",
                    "client_id": client_id,
                    "limit": info.get("limit"),
                    "reset": info.get("reset"),
                    "retry_after": info.get("retry_after")
                },
                headers={
                    "Retry-After": str(info.get("retry_after", 60)),
                    "X-RateLimit-Limit": str(info.get("limit", 0)),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": info.get("reset", "")
                }
            )

        # Add rate limit headers to response
        response = await call_next(request)

        # Get minute info for headers
        minute_info = info.get("minute", {})
        if minute_info:
            response.headers["X-RateLimit-Limit"] = str(minute_info.get("limit", 0))
            response.headers["X-RateLimit-Remaining"] = str(minute_info.get("remaining", 0))
            if minute_info.get("reset"):
                response.headers["X-RateLimit-Reset"] = minute_info["reset"]

        return response


def create_rate_limiter(redis_url: Optional[str] = None, config: Optional[RateLimitConfig] = None):
    """
    Create rate limiter middleware

    Args:
        redis_url: Redis connection URL
        config: Rate limit configuration

    Returns:
        RateLimitMiddleware instance
    """
    redis_client = None

    if redis_url:
        try:
            import redis.asyncio as redis
            redis_client = redis.from_url(redis_url, decode_responses=True)
            logger.info(f"Connected to Redis for rate limiting")
        except ImportError:
            logger.warning("redis package not installed, using in-memory rate limiting")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")

    return RateLimitMiddleware(redis_client, config)
