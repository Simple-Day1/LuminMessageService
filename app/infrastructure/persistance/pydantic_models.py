from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from LuminMessageService.app.domain.models.common.value_objects import MessageText


class MessageTextxModel(BaseModel):
    value: str


class CreateMessageRequest(BaseModel):
    message_id: UUID
    sender_id: UUID
    recipient_id: UUID
    chat_id: UUID
    text: MessageText
    sent_at: datetime | None = None
    read_at: datetime | None = None
    edited_at: datetime | None = None
