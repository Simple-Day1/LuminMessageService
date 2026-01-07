from taskiq_nats import NatsBroker
from typing import Any


class TaskiqTaskManager:
    def __init__(self, broker: NatsBroker):
        self.broker = broker

    async def execute_command(self, command_type: str, command_data: dict[str, Any]) -> dict[str, Any]:
        pass


_taskiq_broker = None


def get_taskiq_broker() -> NatsBroker:
    global _taskiq_broker
    if _taskiq_broker is None:
        _taskiq_broker = NatsBroker(
            "nats://localhost:4222",
            queue="message_service_queue"
        )
    return _taskiq_broker
