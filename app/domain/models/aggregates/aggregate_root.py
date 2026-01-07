from uuid import UUID, uuid4
from abc import ABC
from datetime import datetime
from LuminMessageService.app.domain.events.domain_event import DomainEvent


class AggregateRoot(ABC):
    def __init__(self, aggregate_id: UUID = None):
        self._id: UUID = aggregate_id or self._generate_id()
        self._version: int = 0
        self._domain_events: list[DomainEvent] = []
        self._created_at: datetime = datetime.now()
        self._updated_at: datetime = self._created_at
        self._expected_version: int = 0

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def version(self) -> int:
        return self._version

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    @staticmethod
    def _generate_id() -> UUID:
        return uuid4()

    def add_domain_event(self, event: "DomainEvent") -> None:
        if not hasattr(event, "aggregate_id"):
            event.aggregate_id = self.id
        self._domain_events.append(event)

    def get_domain_events(self) -> list["DomainEvent"]:
        return self._domain_events.copy()

    def clear_domain_events(self) -> None:
        self._domain_events.clear()

    def _increment_version(self) -> None:
        self._version += 1
        self._updated_at = datetime.now()

    def validate_invariants(self) -> None:
        pass

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AggregateRoot):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash((self.id, type(self).__name__))

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id} version={self.version}>"
