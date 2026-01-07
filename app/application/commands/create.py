from datetime import datetime
from typing import Any
from uuid import UUID
from dataclasses import dataclass
from LuminMessageService.app.application.services.message_service import MessageService
from LuminMessageService.app.domain.events.event_bus import EventBus
from LuminMessageService.app.domain.models.aggregates.message import Message
from LuminMessageService.app.domain.models.common.value_objects import MessageText


@dataclass
class CreateMessageCommand:
    message_id: UUID
    sender_id: UUID
    recipient_id: UUID
    chat_id: UUID
    text: MessageText
    sent_at: datetime | None = None
    read_at: datetime | None = None
    edited_at: datetime | None = None


class CreateMessageHandler:
    def __init__(self, message_service: MessageService, event_bus: EventBus) -> None:
        self.message_service: MessageService = message_service
        self.event_bus: EventBus = event_bus

    async def handle(self, command: CreateMessageCommand) -> dict[str, Any]:
        try:
            message: Message = await self.message_service.create_message(
                message_id=command.message_id,
                sender_id=command.sender_id,
                recipient_id=command.recipient_id,
                chat_id=command.chat_id,
                text=command.text,
                sent_at=command.sent_at,
                read_at=command.read_at,
                edited_at=command.edited_at
            )
            await self.event_bus.process_events(message)
            return {
                "success": True,
                "message_id": command.message_id
            }

        except Exception as e:
            return {
                "success": False,
                "exception": str(e)
            }
