"""Simple in-memory cache with TTL and retry logic."""
import time
from functools import wraps
from typing import Any, Callable, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class TTLCache:
    """Thread-safe in-memory cache with TTL expiration."""

    def __init__(self, ttl_seconds: int = 300):
        self.ttl = ttl_seconds
        self._store: Dict[str, tuple] = {}

    def get(self, key: str) -> Optional[Any]:
        """Get value if exists and not expired."""
        if key not in self._store:
            return None
        value, timestamp = self._store[key]
        if time.time() - timestamp > self.ttl:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any) -> None:
        """Set value with current timestamp."""
        self._store[key] = (value, time.time())

    def clear(self) -> None:
        """Clear all entries."""
        self._store.clear()


_cache = TTLCache(ttl_seconds=300)


def cached(ttl_seconds: int = 300):
    """Decorator to cache function result with TTL."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Simple cache key: function name + string repr of args/kwargs
            key = f"{func.__name__}_{str(args)}_{str(sorted(kwargs.items()))}"
            cached_val = _cache.get(key)
            if cached_val is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_val
            result = func(*args, **kwargs)
            _cache.set(key, result)
            return result

        return wrapper

    return decorator


def retry(max_attempts: int = 3, backoff_factor: float = 1.5, jitter: bool = True):
    """Decorator to retry function with exponential backoff."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            attempt = 0
            delay = 1
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                    if attempt >= max_attempts:
                        logger.error(f"{func.__name__} failed after {max_attempts} attempts: {e}")
                        raise
                    if jitter:
                        import random

                        delay = delay * backoff_factor + random.uniform(0, 0.1)
                    else:
                        delay = delay * backoff_factor
                    logger.warning(f"{func.__name__} attempt {attempt} failed, retrying in {delay:.2f}s: {e}")
                    time.sleep(delay)

        return wrapper

    return decorator
