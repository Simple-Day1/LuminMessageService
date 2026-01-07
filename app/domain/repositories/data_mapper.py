from abc import ABC, abstractmethod
from LuminMessageService.app.domain.models.aggregates.message import Message


class MessageDataMapper(ABC):
    @abstractmethod
    def to_domain(self, data: dict) -> Message:
        pass

    @abstractmethod
    def to_persistence(self, message: Message) -> dict:
        pass

    @abstractmethod
    def to_domain_list(self, data_list: list[dict]) -> list[Message]:
        pass
