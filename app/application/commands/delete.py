from typing import Any
from uuid import UUID
from dataclasses import dataclass
from LuminMessageService.app.application.services.message_service import MessageService
from LuminMessageService.app.domain.events.event_bus import EventBus


@dataclass
class DeleteMessageCommand:
    message_id: UUID


class DeleteMessageHandler:
    def __init__(self, message_service: MessageService, event_bus: EventBus) -> None:
        self.message_service: MessageService = message_service
        self.event_bus: EventBus = event_bus

    async def handle(self, command: DeleteMessageCommand) -> dict[str, Any]:
        try:
            await self.message_service.delete(command.message_id)
            return {
                "success": True,
                "message_id": command.message_id
            }

        except Exception as e:
            return {
                "success": False,
                "exception": str(e)
            }
