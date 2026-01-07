from typing import Any
from LuminMessageService.app.domain.models.aggregates.message import Message
from LuminMessageService.app.domain.repositories.data_mapper import MessageDataMapper


class MessageMapper(MessageDataMapper):
    def to_domain(self, data: dict) -> Message:
        try:
            message = Message(
                message_id=data["message_id"],
                sender_id=data["sender_id"],
                recipient_id=data["recipient_id"],
                chat_id=data["chat_id"],
                text=data["text"],
                sent_at=data["sent_at"],
                read_at=data["read_at"],
                edited_at=data["edited_at"],
            )

            return message

        except Exception as e:
            raise ValueError(f"Error mapping to domain: {e}")

    def to_persistence(self, message: Message) -> dict[str, Any]:
        try:

            return {
                "message_id": message.id,
                "sender_id": message.sender_id,
                "recipient_id": message.recipient_id,
                "chat_id": message.chat_id,
                "text": message.text.value,
                "sent_at": message.sent_at,
                "read_at": message.read_at,
                "edited_at": message.edited_at,
            }
        except Exception as e:
            raise ValueError(f"Error mapping to persistence: {e}")

    def to_domain_list(self, data_list: list[dict]) -> list[Message]:
        return [self.to_domain(data) for data in data_list]
