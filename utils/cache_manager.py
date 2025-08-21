"""
Simple in-memory cache for LLM responses and vector search results.
Provides significant performance improvements for repeated queries.
"""
import hashlib
import time
from typing import Dict, Any, Optional, Tuple
from functools import wraps

class SimpleCache:
    """Thread-safe in-memory cache with TTL support"""
    
    def __init__(self, max_size: int = 100, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: Dict[str, Tuple[Any, float]] = {}
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        key_data = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        if key in self.cache:
            value, expiry = self.cache[key]
            if time.time() < expiry:
                return value
            else:
                # Remove expired entry
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL"""
        if ttl is None:
            ttl = self.default_ttl
        
        # Remove oldest entries if cache is full
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]
        
        expiry = time.time() + ttl
        self.cache[key] = (value, expiry)
    
    def clear(self) -> None:
        """Clear all cache entries"""
        self.cache.clear()
    
    def size(self) -> int:
        """Get current cache size"""
        return len(self.cache)

# Global cache instances
llm_cache = SimpleCache(max_size=100, default_ttl=1800)  # 30 minutes TTL
vector_cache = SimpleCache(max_size=50, default_ttl=3600)  # 1 hour TTL

def cache_llm_response(func):
    """Decorator to cache LLM responses"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Generate cache key
        cache_key = llm_cache._generate_key(*args, **kwargs)
        
        # Try to get from cache
        cached_result = llm_cache.get(cache_key)
        if cached_result is not None:
            print(f"Cache hit for LLM request")
            return cached_result
        
        # Call original function
        result = func(*args, **kwargs)
        
        # Cache the result
        llm_cache.set(cache_key, result)
        print(f"Cached LLM response (cache size: {llm_cache.size()})")
        
        return result
    return wrapper

def cache_vector_search(func):
    """Decorator to cache vector search results"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Generate cache key
        cache_key = vector_cache._generate_key(*args, **kwargs)
        
        # Try to get from cache
        cached_result = vector_cache.get(cache_key)
        if cached_result is not None:
            print(f"Cache hit for vector search")
            return cached_result
        
        # Call original function
        result = func(*args, **kwargs)
        
        # Cache the result
        vector_cache.set(cache_key, result)
        print(f"Cached vector search result (cache size: {vector_cache.size()})")
        
        return result
    return wrapper
