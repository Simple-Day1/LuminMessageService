from typing import Any
from uuid import UUID
from dataclasses import dataclass
from LuminMessageService.app.application.services.message_service import MessageService
from LuminMessageService.app.domain.events.event_bus import EventBus
from LuminMessageService.app.domain.models.common.value_objects import MessageText


@dataclass
class EditMessageTextCommand:
    message_id: UUID
    new_text: MessageText


class EditMessageTextHandler:
    def __init__(self, message_service: MessageService, event_bus: EventBus) -> None:
        self.message_service: MessageService = message_service
        self.event_bus: EventBus = event_bus

    async def handle(self, command: EditMessageTextCommand) -> dict[str, Any]:
        try:
            await self.message_service.edit_message_text(command.message_id, command.new_text)
            return {
                "success": True,
                "message_id": command.message_id,
                "new_text": command.new_text
            }

        except Exception as e:
            return {
                "success": False,
                "exception": str(e)
            }
