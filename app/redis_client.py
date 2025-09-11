import os
import json
from typing import Optional, Any
from dotenv import load_dotenv
import redis
from redis.exceptions import ConnectionError, RedisError

load_dotenv()

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))  # Default 5 minutes

# Global Redis client instance
redis_client = None

def get_redis_client() -> Optional[redis.Redis]:
    """Get Redis client instance with connection pooling"""
    global redis_client
    if redis_client is None:
        try:
            redis_client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                password=REDIS_PASSWORD,
                db=REDIS_DB,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            # Test connection
            redis_client.ping()
        except (ConnectionError, RedisError) as e:
            print(f"Redis connection failed: {e}")
            redis_client = None
    return redis_client

class CacheService:
    """Service for caching operations with fallback when Redis is unavailable"""
    
    def __init__(self):
        self.client = get_redis_client()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.client:
            return None
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
        except (RedisError, json.JSONDecodeError) as e:
            print(f"Cache get error for key {key}: {e}")
        return None
    
    def set(self, key: str, value: Any, ttl: int = CACHE_TTL) -> bool:
        """Set value in cache with TTL"""
        if not self.client:
            return False
        try:
            serialized_value = json.dumps(value, default=str)
            return self.client.setex(key, ttl, serialized_value)
        except (RedisError, TypeError) as e:
            print(f"Cache set error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.client:
            return False
        try:
            return bool(self.client.delete(key))
        except RedisError as e:
            print(f"Cache delete error for key {key}: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        if not self.client:
            return 0
        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
        except RedisError as e:
            print(f"Cache delete pattern error for pattern {pattern}: {e}")
        return 0

# Global cache service instance
cache_service = CacheService()

def get_cache_service() -> CacheService:
    """Dependency injection for cache service"""
    return cache_service