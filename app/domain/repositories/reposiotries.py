from abc import ABC, abstractmethod
from uuid import UUID
from LuminMessageService.app.domain.models.aggregates.message import Message


class MessageRepository(ABC):
    @abstractmethod
    def save(self, message: Message) -> None:
        pass

    @abstractmethod
    def get_by_id(self, message_id: UUID) -> Message | None:
        pass

    @abstractmethod
    def delete(self, message_id: UUID) -> None:
        pass
