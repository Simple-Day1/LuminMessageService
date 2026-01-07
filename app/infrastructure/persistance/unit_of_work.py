from contextlib import asynccontextmanager
from typing import Self, AsyncGenerator
from LuminMessageService.app.domain.repositories.unit_of_work import UnitOfWork
from LuminMessageService.app.infrastructure.cache.multi_level_cache import MultiLevelCache
from LuminMessageService.app.infrastructure.persistance.identity_map import MessageIdentityMap
from LuminMessageService.app.infrastructure.persistance.postgres_sql_message_repository import \
    PostgresSQLMessageRepository


class MessageUnitOfWork(UnitOfWork):
    def __init__(self, connection_factory, cache: MultiLevelCache) -> None:
        self.connection_factory = connection_factory
        self.identity_map: MessageIdentityMap = MessageIdentityMap()
        self.cache = cache

    async def __aenter__(self) -> Self:
        self.messages = PostgresSQLMessageRepository(
            connection_factory=self.connection_factory,
            identity_map=self.identity_map,
            cache=self.cache
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        self.identity_map.clear()

    async def commit(self) -> None:
        pass

    async def rollback(self) -> None:
        self.identity_map.clear()


@asynccontextmanager
async def get_unit_of_work(connection_factory, cache: MultiLevelCache) -> AsyncGenerator[MessageUnitOfWork, None]:
    uow = MessageUnitOfWork(connection_factory, cache)
    async with uow:
        yield uow
