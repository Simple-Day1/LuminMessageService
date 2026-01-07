import uuid
from datetime import datetime
from typing import Any, Dict
from dataclasses import dataclass, asdict


@dataclass
class DomainEvent:
    event_type: str
    aggregate_id: uuid.UUID
    data: Dict[str, Any]
    occurred_at: datetime = None
    version: int = 1

    def __post_init__(self):
        if self.occurred_at is None:
            self.occurred_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['occurred_at'] = self.occurred_at.isoformat()
        result['aggregate_id'] = str(self.aggregate_id)
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DomainEvent":
        if isinstance(data['occurred_at'], str):
            data['occurred_at'] = datetime.fromisoformat(data['occurred_at'])
        if isinstance(data['aggregate_id'], str):
            data['aggregate_id'] = uuid.UUID(data['aggregate_id'])
        return cls(**data)
