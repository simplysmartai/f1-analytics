"""Advanced caching strategies and utilities"""
from typing import Callable, Any, Optional, Dict, TypeVar
from functools import wraps
from datetime import datetime, timedelta
import hashlib
import json
from utils.logger import logger
from utils.performance import monitor

T = TypeVar('T')


class CacheEntry:
    """Single cache entry with expiration"""
    
    def __init__(self, value: Any, ttl_seconds: Optional[int] = None):
        """
        Initialize cache entry.
        
        Args:
            value: Value to cache
            ttl_seconds: Time to live in seconds (None = no expiration)
        """
        self.value = value
        self.created_at = datetime.now()
        self.ttl_seconds = ttl_seconds
        self.access_count = 0
        self.last_accessed = datetime.now()
    
    def is_expired(self) -> bool:
        """Check if entry is expired"""
        if self.ttl_seconds is None:
            return False
        
        elapsed = (datetime.now() - self.created_at).total_seconds()
        return elapsed > self.ttl_seconds
    
    def access(self) -> Any:
        """Access the value and update metrics"""
        self.access_count += 1
        self.last_accessed = datetime.now()
        return self.value


class SmartCache:
    """Smart caching with TTL, LRU eviction, and statistics"""
    
    def __init__(self, max_size: int = 1000, default_ttl: Optional[int] = None):
        """
        Initialize smart cache.
        
        Args:
            max_size: Maximum number of entries
            default_ttl: Default TTL in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: Dict[str, CacheEntry] = {}
        self.hits = 0
        self.misses = 0
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        try:
            # Convert all arguments to strings and hash
            key_parts = [str(arg) for arg in args]
            key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
            key_str = "|".join(key_parts)
            return hashlib.md5(key_str.encode()).hexdigest()
        except Exception as e:
            logger.warning(f"Failed to generate cache key: {e}")
            return None
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        if key not in self.cache:
            self.misses += 1
            monitor.record_cache_miss()
            return None
        
        entry = self.cache[key]
        
        # Check expiration
        if entry.is_expired():
            logger.debug(f"Cache entry expired: {key}")
            del self.cache[key]
            self.misses += 1
            monitor.record_cache_miss()
            return None
        
        value = entry.access()
        self.hits += 1
        monitor.record_cache_hit()
        logger.debug(f"Cache hit: {key} (access #{entry.access_count})")
        return value
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: TTL override (None = use default)
        """
        # Use provided TTL or default
        actual_ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        
        # Remove oldest entry if cache is full
        if len(self.cache) >= self.max_size:
            self._evict_lru()
        
        self.cache[key] = CacheEntry(value, actual_ttl)
        logger.debug(f"Cache set: {key} (TTL: {actual_ttl}s)")
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry"""
        if not self.cache:
            return
        
        # Find LRU entry
        lru_key = min(
            self.cache.keys(),
            key=lambda k: self.cache[k].last_accessed
        )
        
        del self.cache[lru_key]
        logger.debug(f"Evicted LRU entry: {lru_key}")
    
    def clear(self) -> None:
        """Clear all cache entries"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
        logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{hit_rate:.1f}%",
            "total_accesses": total
        }


def cached(ttl_seconds: Optional[int] = None) -> Callable:
    """
    Decorator for caching function results with TTL.
    
    Args:
        ttl_seconds: Time to live in seconds
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        cache = SmartCache(default_ttl=ttl_seconds)
        
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            # Generate cache key
            key = cache._generate_key(*args, **kwargs)
            if key is None:
                # Cache key generation failed, call function directly
                return func(*args, **kwargs)
            
            # Try to get from cache
            cached_value = cache.get(key)
            if cached_value is not None:
                logger.debug(f"Returning cached value for {func.__name__}")
                return cached_value
            
            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(key, result)
            return result
        
        # Attach cache object for inspection
        wrapper.cache = cache
        return wrapper
    
    return decorator


# Global cache instance for shared caching
global_cache = SmartCache(max_size=500, default_ttl=3600)
