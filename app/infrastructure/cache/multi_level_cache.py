from typing import Optional, Any
from uuid import UUID
from datetime import timedelta
import logging
from LuminMessageService.app.domain.models.aggregates.message import Message
from LuminMessageService.app.infrastructure.cache.redis_cache import RedisCache
from LuminMessageService.app.infrastructure.persistance.identity_map import MessageIdentityMap
from LuminMessageService.app.infrastructure.persistance.message_mapper import MessageMapper

logger = logging.getLogger(__name__)


class MultiLevelCache:
    def __init__(self, redis_cache: RedisCache, identity_map: MessageIdentityMap):
        self.redis = redis_cache
        self.identity_map = identity_map
        self.local_cache_ttl = timedelta(minutes=5)

    async def get_message(self, message_id: UUID) -> Optional[Message]:
        cached_user = self.identity_map.get(message_id)
        if cached_user:
            logger.debug(f"Message {message_id} found in Identity Map")
            return cached_user

        redis_message_data = await self.redis.get_message(message_id)
        if redis_message_data:
            redis_message = MessageMapper().to_domain(data=redis_message_data)
        else:
            redis_message = None

        if redis_message:
            logger.debug(f"Message {message_id} found in Redis")
            if hasattr(redis_message, '__dict__'):
                self.identity_map.add(redis_message)
            return redis_message

        logger.debug(f"Message {message_id} not found in cache")
        return None

    async def set_message(self, message_id: UUID, message_data: dict) -> bool:
        try:
            self.identity_map.add(MessageMapper().to_domain(message_data))

            ttl = 3600
            success = await self.redis.set_message(message_id, message_data, ttl)

            if success:
                logger.debug(f"Message {message_id} cached in Redis")
            else:
                logger.warning(f"Failed to cache message {message_id} in Redis")

            return success
        except Exception as e:
            logger.error(f"Error caching message {message_id}: {e}")
            return False

    async def invalidate_message(self, message_id: UUID) -> bool:
        try:
            self.identity_map.remove(message_id)

            success = await self.redis.delete_message(message_id)

            await self.redis.invalidate_message_cache(message_id)

            logger.debug(f"Cache invalidated for message {message_id}")
            return success
        except Exception as e:
            logger.error(f"Error invalidating cache for message {message_id}: {e}")
            return False

    async def get_with_fallback(
            self,
            message_id: UUID,
            fallback_func,
            *args, **kwargs
    ) -> Optional[Any]:
        cached_data = await self.get_message(message_id)

        if cached_data:
            return cached_data

        fresh_data = await fallback_func(*args, **kwargs)

        if fresh_data:
            await self.set_message(message_id, fresh_data)

        return fresh_data
