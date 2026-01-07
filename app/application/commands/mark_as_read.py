from typing import Any
from uuid import UUID
from dataclasses import dataclass
from LuminMessageService.app.application.services.message_service import MessageService
from LuminMessageService.app.domain.events.event_bus import EventBus


@dataclass
class MarkMessageAsReadCommand:
    message_id: UUID


class MarkMessageAsReadHandler:
    def __init__(self, message_service: MessageService, event_bus: EventBus) -> None:
        self.message_service: MessageService = message_service
        self.event_bus: EventBus = event_bus

    async def handle(self, command: MarkMessageAsReadCommand) -> dict[str, Any]:
        try:
            await self.message_service.mark_message_as_read(command.message_id)
            return {
                "success": True,
                "message_id": command.message_id
            }
        except Exception as e:
            return {
                "success": False,
                "exception": str(e)
            }
