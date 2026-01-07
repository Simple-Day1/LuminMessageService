from threading import Lock
from uuid import UUID
from LuminMessageService.app.domain.models.aggregates.message import Message
from LuminMessageService.app.domain.repositories.identity_map import IdentityMap


class MessageIdentityMap(IdentityMap):
    def __init__(self) -> None:
        self._map: dict[UUID, Message] = {}
        self._lock = Lock()

    def add(self, message: Message) -> None:
        with self._lock:
            self._map[message.id] = message

    def get(self, message_id: UUID) -> Message | None:
        with self._lock:
            return self._map.get(message_id)

    def remove(self, message_id: UUID) -> None:
        with self._lock:
            del self._map[message_id]

    def clear(self) -> None:
        with self._lock:
            self._map.clear()

    def contains(self, message_id: UUID) -> bool:
        with self._lock:
            return message_id in self._map

    def get_all(self) -> dict[UUID, Message]:
        with self._lock:
            return self._map.copy()
