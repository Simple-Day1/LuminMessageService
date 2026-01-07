from abc import ABC, abstractmethod
from typing import Callable, Type
from LuminMessageService.app.domain.events.domain_event import DomainEvent
from LuminMessageService.app.domain.models.aggregates.message import Message


class EventBus(ABC):
    @abstractmethod
    def publish(self, event: DomainEvent) -> None:
        pass

    @abstractmethod
    def subscribe(self, event_type: Type[DomainEvent], handler: Callable) -> None:
        pass

    @abstractmethod
    async def process_events(self, aggregate: Message) -> None:
        pass
