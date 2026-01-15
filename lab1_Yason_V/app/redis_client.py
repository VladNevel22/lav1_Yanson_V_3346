import redis
import json
from typing import Optional, Any, Union
import os
from datetime import timedelta

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

class RedisCache:
    def __init__(self):
        self.client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            password=REDIS_PASSWORD,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_keepalive=True
        )
    
    def get(self, key: str) -> Optional[Any]:
        """Получить значение по ключу"""
        try:
            value = self.client.get(key)
            return json.loads(value) if value else None
        except (redis.RedisError, json.JSONDecodeError):
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Установить значение с TTL (в секундах)"""
        try:
            serialized = json.dumps(value, default=str)
            if ttl:
                return self.client.setex(key, ttl, serialized)
            return self.client.set(key, serialized)
        except (redis.RedisError, TypeError):
            return False
    
    def delete(self, key: str) -> bool:
        """Удалить ключ"""
        try:
            return bool(self.client.delete(key))
        except redis.RedisError:
            return False
    
    def exists(self, key: str) -> bool:
        """Проверить существование ключа"""
        try:
            return bool(self.client.exists(key))
        except redis.RedisError:
            return False
    
    def flush_all(self):
        """Очистить весь кэш (только для разработки)"""
        try:
            self.client.flushdb()
        except redis.RedisError:
            pass
    
    def ping(self) -> bool:
        """Проверить соединение с Redis"""
        try:
            return self.client.ping()
        except redis.RedisError:
            return False



cache = RedisCache()