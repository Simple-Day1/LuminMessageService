import pickle
from typing import Optional, Any
from uuid import UUID
import redis.asyncio as redis
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class CacheConfig:
    host: str = "localhost"
    port: int = 6379
    password: Optional[str] = None
    db: int = 0
    default_ttl: int = 3600
    key_prefix: str = "message_service:"


class RedisCache:
    def __init__(self, config: CacheConfig):
        self.config = config
        self._client: Optional[redis.Redis] = None
        self._connected = False

    async def connect(self) -> None:
        if not self._connected:
            self._client = redis.Redis(
                host=self.config.host,
                port=self.config.port,
                password=self.config.password,
                db=self.config.db,
                decode_responses=False,
                socket_connect_timeout=5,
                socket_keepalive=True
            )
            try:
                await self._client.ping()
                self._connected = True
                logger.info("✅ Redis connected successfully")
            except Exception as e:
                logger.error(f"❌ Redis connection failed: {e}")
                raise

    async def disconnect(self) -> None:
        if self._client and self._connected:
            await self._client.close()
            self._connected = False

    def _build_key(self, key: str) -> str:
        return f"{self.config.key_prefix}{key}"

    async def get(self, key: str) -> Optional[Any]:
        if not self._connected:
            return None

        try:
            full_key = self._build_key(key)
            data = await self._client.get(full_key)
            if data:
                return pickle.loads(data)
            return None
        except Exception as e:
            logger.error(f"Redis get error for key {key}: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        if not self._connected:
            return False

        try:
            full_key = self._build_key(key)
            serialized = pickle.dumps(value)
            ttl = ttl or self.config.default_ttl
            await self._client.setex(full_key, ttl, serialized)
            return True
        except Exception as e:
            logger.error(f"Redis set error for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        if not self._connected:
            return False

        try:
            full_key = self._build_key(key)
            await self._client.delete(full_key)
            return True
        except Exception as e:
            logger.error(f"Redis delete error for key {key}: {e}")
            return False

    async def delete_pattern(self, pattern: str) -> bool:
        if not self._connected:
            return False

        try:
            full_pattern = self._build_key(pattern)
            keys = await self._client.keys(full_pattern)
            if keys:
                await self._client.delete(*keys)
            return True
        except Exception as e:
            logger.error(f"Redis delete pattern error: {e}")
            return False

    async def get_message(self, message_id: UUID) -> Optional[dict]:
        return await self.get(f"message:{message_id}")

    async def set_message(self, message_id: UUID, message_data: dict, ttl: Optional[int] = None) -> bool:
        return await self.set(f"message:{message_id}", message_data, ttl)

    async def delete_message(self, message_id: UUID) -> bool:
        return await self.delete(f"message:{message_id}")

    async def invalidate_message_cache(self, message_id: UUID) -> bool:
        await self.delete_message(message_id)
        await self.delete_pattern(f"message:{message_id}:*")
        return True
