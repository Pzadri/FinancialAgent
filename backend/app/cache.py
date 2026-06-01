"""Simple in-memory cache with TTL for expensive operations."""
import time
from typing import Any

_cache: dict[str, dict] = {}


def get(key: str) -> Any | None:
    """Get a cached value if it exists and hasn't expired."""
    entry = _cache.get(key)
    if entry is None:
        return None
    if time.time() > entry["expires"]:
        del _cache[key]
        return None
    return entry["value"]


def set(key: str, value: Any, ttl_seconds: int = 300):
    """Cache a value with a TTL (default 5 minutes)."""
    _cache[key] = {
        "value": value,
        "expires": time.time() + ttl_seconds
    }


def invalidate(key: str):
    """Remove a specific key from cache."""
    _cache.pop(key, None)


def invalidate_prefix(prefix: str):
    """Remove all keys starting with a prefix."""
    keys_to_remove = [k for k in _cache if k.startswith(prefix)]
    for k in keys_to_remove:
        del _cache[k]


def clear():
    """Clear all cached data."""
    _cache.clear()
