from abc import ABC, abstractmethod
from uuid import UUID
from LuminMessageService.app.domain.models.aggregates.message import Message


class IdentityMap(ABC):
    @abstractmethod
    def add(self, message: Message) -> None:
        pass

    @abstractmethod
    def get(self, message_id: UUID) -> Message | None:
        pass

    @abstractmethod
    def remove(self, message_id: UUID) -> None:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass

    @abstractmethod
    def contains(self, message_id: UUID) -> bool:
        pass
