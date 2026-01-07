from dataclasses import dataclass
from typing import Any
from uuid import UUID
from LuminMessageService.app.domain.events.domain_event import DomainEvent


@dataclass
class MessageCreatedEvent(DomainEvent):
    def __init__(self, aggregate_id: UUID, data: dict[str, Any]) -> None:
        super().__init__(
            event_type="MessageCreatedEvent",
            aggregate_id=aggregate_id,
            data=data
        )


@dataclass
class MessageSentEvent(DomainEvent):
    def __init__(self, aggregate_id: UUID, data: dict[str, Any]) -> None:
        super().__init__(
            event_type="MessageSentEvent",
            aggregate_id=aggregate_id,
            data=data
        )


@dataclass
class MessageReadEvent(DomainEvent):
    def __init__(self, aggregate_id: UUID, data: dict[str, Any]) -> None:
        super().__init__(
            event_type="MessageReadEvent",
            aggregate_id=aggregate_id,
            data=data
        )


@dataclass
class MessageEditedEvent(DomainEvent):
    def __init__(self, aggregate_id: UUID, data: dict[str, Any]) -> None:
        super().__init__(
            event_type="MessageEditedEvent",
            aggregate_id=aggregate_id,
            data=data
        )
