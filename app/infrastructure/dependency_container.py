from typing import Optional
from LuminMessageService.app.application.commands.create import CreateMessageHandler
from LuminMessageService.app.application.commands.delete import DeleteMessageHandler
from LuminMessageService.app.application.commands.edit_text import EditMessageTextHandler
from LuminMessageService.app.application.commands.mark_as_read import MarkMessageAsReadHandler
from LuminMessageService.app.application.queries.get_by_id import GetMessageByIDHandler
from LuminMessageService.app.application.services.message_service import MessageService
from LuminMessageService.app.infrastructure.cache.multi_level_cache import MultiLevelCache
from LuminMessageService.app.infrastructure.cache.redis_cache import CacheConfig, RedisCache
from LuminMessageService.app.infrastructure.messaging.nats_event_bus import NatsEventBus
from LuminMessageService.app.infrastructure.persistance.identity_map import MessageIdentityMap


class DependencyContainer:
    def __init__(self, connection_factory, redis_config: Optional[CacheConfig] = None):
        self.connection_factory = connection_factory
        self.redis_config = redis_config or CacheConfig()
        self._event_bus = None
        self._message_service = None
        self._redis_cache = None
        self._multi_level_cache = None
        self._handlers = {}
        self._identity_map = None

    async def get_redis_cache(self) -> RedisCache:
        if not self._redis_cache:
            self._redis_cache = RedisCache(self.redis_config)
            await self._redis_cache.connect()
        return self._redis_cache

    def get_identity_map(self) -> MessageIdentityMap:
        if not self._identity_map:
            self._identity_map = MessageIdentityMap()
        return self._identity_map

    async def get_multi_level_cache(self) -> MultiLevelCache:
        if not self._multi_level_cache:
            redis_cache = await self.get_redis_cache()
            identity_map = self.get_identity_map()
            self._multi_level_cache = MultiLevelCache(redis_cache, identity_map)
        return self._multi_level_cache

    async def get_event_bus(self) -> NatsEventBus:
        if not self._event_bus:
            self._event_bus = NatsEventBus()
            await self._event_bus.connect()
        return self._event_bus

    async def get_message_service(self) -> MessageService:
        if not self._message_service:
            cache = await self.get_multi_level_cache()
            self._message_service = MessageService(self.connection_factory, cache)
            print(f"MessageService created with connection_factory: {self.connection_factory}")
        return self._message_service

    async def get_message_by_id_handler(self) -> GetMessageByIDHandler:
        key = "get_message_by_id"
        if key not in self._handlers:
            event_bus = await self.get_event_bus()
            message_service = await self.get_message_service()
            self._handlers[key] = GetMessageByIDHandler(message_service, event_bus)
        return self._handlers[key]

    async def get_create_message_handler(self) -> CreateMessageHandler:
        key = "create_message"
        if key not in self._handlers:
            event_bus = await self.get_event_bus()
            message_service = await self.get_message_service()
            self._handlers[key] = CreateMessageHandler(message_service, event_bus)
        return self._handlers[key]

    async def get_delete_message_handler(self) -> DeleteMessageHandler:
        key = "delete_message"
        if key not in self._handlers:
            event_bus = await self.get_event_bus()
            message_service = await self.get_message_service()
            self._handlers[key] = DeleteMessageHandler(message_service, event_bus)
        return self._handlers[key]

    async def get_edit_message_text_handler(self) -> EditMessageTextHandler:
        key = "edit_message_text"
        if key not in self._handlers:
            event_bus = await self.get_event_bus()
            message_service = await self.get_message_service()
            self._handlers[key] = EditMessageTextHandler(message_service, event_bus)
        return self._handlers[key]

    async def get_mark_message_as_read_handler(self) -> MarkMessageAsReadHandler:
        key = "mark_message_as_read"
        if key not in self._handlers:
            event_bus = await self.get_event_bus()
            message_service = await self.get_message_service()
            self._handlers[key] = MarkMessageAsReadHandler(message_service, event_bus)
        return self._handlers[key]
