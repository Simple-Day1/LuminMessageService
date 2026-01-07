from datetime import datetime
from uuid import UUID
from LuminMessageService.app.domain.events.message_events import MessageCreatedEvent
from LuminMessageService.app.domain.models.aggregates.message import Message
from LuminMessageService.app.domain.models.common.value_objects import MessageText
from LuminMessageService.app.infrastructure.cache.multi_level_cache import MultiLevelCache
from LuminMessageService.app.infrastructure.persistance.unit_of_work import get_unit_of_work


class MessageService:
    def __init__(self, connection_factory, cache: MultiLevelCache) -> None:
        self.connection_factory = connection_factory
        self.cache = cache

    async def create_message(
            self,
            message_id: UUID,
            sender_id: UUID,
            recipient_id: UUID,
            chat_id: UUID,
            text: MessageText,
            sent_at: datetime | None = None,
            read_at: datetime | None = None,
            edited_at: datetime | None = None,
    ) -> Message:
        async with get_unit_of_work(self.connection_factory, self.cache) as uow:
            existing_message = await uow.messages.get_by_id(message_id)
            if existing_message:
                raise ValueError(f"Message {message_id} already exists")

            message = Message(
                message_id=message_id,
                sender_id=sender_id,
                recipient_id=recipient_id,
                chat_id=chat_id,
                text=text,
                sent_at=sent_at,
                read_at=read_at,
                edited_at=edited_at,
            )

            message.add_domain_event(MessageCreatedEvent(
                aggregate_id=message_id,
                data={
                    "sender_id": sender_id,
                    "recipient_id": recipient_id,
                    "chat_id": chat_id,
                    "text": text.value,
                    "sent_at": sent_at,
                    "read_at": read_at,
                    "edited_at": edited_at,
                }

            ))

            await uow.messages.save(message)
            await uow.commit()

            print(f"User created: {message_id}")
            return message

    async def get_message_by_id(self, message_id: UUID) -> Message | None:
        async with get_unit_of_work(self.connection_factory, self.cache) as uow:
            message: Message = await uow.messages.get_by_id(message_id)
            if message:
                print(f"[MessageService.get_message_by_id] Message found: {message}")
                print(f"[MessageService.get_message_by_id] Message class: {message.__class__}")
                print(f"[MessageService.get_message_by_id] Has id attr: {hasattr(message, 'id')}")
                print(f"[MessageService.get_message_by_id] Message.id value: {message.id if hasattr(message, 'id') else 'NO ID'}")
            else:
                print(f"[MessageService.get_message_by_id] Message not found: {message_id}")
                raise ValueError(f"Message {message_id} not found")

            return message

    async def edit_message_text(self, message_id: UUID, new_text: MessageText) -> Message:
        async with get_unit_of_work(self.connection_factory, self.cache) as uow:
            message: Message = await uow.messages.get_by_id(message_id)
            if message:
                print(f"[MessageService.edit_message_text] Message found: {message}")
                print(f"[MessageService.edit_message_text] Message class: {message.__class__}")
                print(f"[MessageService.edit_message_text] Has id attr: {hasattr(message, 'id')}")
                print(
                    f"[MessageService.edit_message_text] Message.id value: {message.id if hasattr(message, 'id') else 'NO ID'}")
                message.edit_text(new_text, datetime.now())
                await uow.messages.save(message)
            else:
                print(f"[MessageService.edit_message_text] Message not found: {message_id}")
                raise ValueError(f"Message {message_id} not found")

            return message

    async def mark_message_as_read(self, message_id: UUID) -> Message:
        async with get_unit_of_work(self.connection_factory, self.cache) as uow:
            message: Message = await uow.messages.get_by_id(message_id)
            if message:
                print(f"[MessageService.mark_message_as_read] Message found: {message}")
                print(f"[MessageService.mark_message_as_read] Message class: {message.__class__}")
                print(f"[MessageService.mark_message_as_read] Has id attr: {hasattr(message, 'id')}")
                print(
                    f"[MessageService.mark_message_as_read] Message.id value: {message.id if hasattr(message, 'id') else 'NO ID'}")
                message.mark_as_read(datetime.now())
                await uow.messages.save(message)
            else:
                print(f"[MessageService.mark_message_as_read] Message not found: {message_id}")
                raise ValueError(f"Message {message_id} not found")

            return message

    async def delete(self, message_id: UUID) -> None:
        async with get_unit_of_work(self.connection_factory, self.cache) as uow:
            await uow.messages.delete(message_id)
            await uow.commit()
