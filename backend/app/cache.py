"""
Caching utilities for query results and embeddings.
Phase 4: API Development - Performance Optimization
Uses cachetools (FREE, in-memory caching).
"""

import hashlib
import json
from typing import Optional, Any, Dict
from functools import wraps
from cachetools import TTLCache
import time

# Cache configuration
QUERY_CACHE_SIZE = 1000  # Maximum number of cached queries
QUERY_CACHE_TTL = 3600   # 1 hour TTL for query results
EMBEDDING_CACHE_SIZE = 500  # Maximum number of cached embeddings
EMBEDDING_CACHE_TTL = 3600  # 1 hour TTL for embeddings

# Initialize caches
query_cache: TTLCache = TTLCache(maxsize=QUERY_CACHE_SIZE, ttl=QUERY_CACHE_TTL)
embedding_cache: TTLCache = TTLCache(maxsize=EMBEDDING_CACHE_SIZE, ttl=EMBEDDING_CACHE_TTL)


def generate_cache_key(query: str, prefix: str = "query") -> str:
    """Generate a cache key from a query string."""
    # Normalize query (lowercase, strip whitespace)
    normalized = query.lower().strip()
    # Create hash for consistent key
    key_hash = hashlib.md5(normalized.encode('utf-8')).hexdigest()
    return f"{prefix}:{key_hash}"


def get_cached_query(query: str) -> Optional[Dict[str, Any]]:
    """
    Get cached query result if available.
    
    Args:
        query: User query string
        
    Returns:
        Cached result dict or None if not found
    """
    cache_key = generate_cache_key(query, "query")
    return query_cache.get(cache_key)


def cache_query_result(query: str, result: Dict[str, Any]) -> None:
    """
    Cache a query result.
    
    Args:
        query: User query string
        result: Query result dictionary
    """
    cache_key = generate_cache_key(query, "query")
    query_cache[cache_key] = result


def get_cached_embedding(text: str) -> Optional[Any]:
    """
    Get cached embedding if available.
    
    Args:
        text: Text to get embedding for
        
    Returns:
        Cached embedding array or None if not found
    """
    cache_key = generate_cache_key(text, "embedding")
    return embedding_cache.get(cache_key)


def cache_embedding(text: str, embedding: Any) -> None:
    """
    Cache an embedding.
    
    Args:
        text: Text that was embedded
        embedding: Embedding array
    """
    cache_key = generate_cache_key(text, "embedding")
    embedding_cache[cache_key] = embedding


def clear_cache() -> Dict[str, int]:
    """
    Clear all caches.
    
    Returns:
        Dictionary with cache sizes before clearing
    """
    query_size = len(query_cache)
    embedding_size = len(embedding_cache)
    
    query_cache.clear()
    embedding_cache.clear()
    
    return {
        "query_cache_cleared": query_size,
        "embedding_cache_cleared": embedding_size
    }


def get_cache_stats() -> Dict[str, Any]:
    """
    Get cache statistics.
    
    Returns:
        Dictionary with cache statistics
    """
    return {
        "query_cache": {
            "size": len(query_cache),
            "max_size": QUERY_CACHE_SIZE,
            "ttl_seconds": QUERY_CACHE_TTL,
            "usage_percent": round((len(query_cache) / QUERY_CACHE_SIZE) * 100, 2)
        },
        "embedding_cache": {
            "size": len(embedding_cache),
            "max_size": EMBEDDING_CACHE_SIZE,
            "ttl_seconds": EMBEDDING_CACHE_TTL,
            "usage_percent": round((len(embedding_cache) / EMBEDDING_CACHE_SIZE) * 100, 2)
        }
    }

