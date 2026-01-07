from datetime import datetime
from uuid import UUID, uuid4
from LuminMessageService.app.domain.events.message_events import MessageSentEvent, MessageReadEvent, MessageEditedEvent
from LuminMessageService.app.domain.models.aggregates.aggregate_root import AggregateRoot
from LuminMessageService.app.domain.models.common.exceptions import (SenderIDCannotBeEmptyError,
                                                                     RecipientIDCannotBeEmptyError,
                                                                     ChatIDCannotBeEmptyError,
                                                                     MessageTextCannotBeEmptyError,
                                                                     CannotSendMessageToYourselfError,
                                                                     CannotReadDeletedMessageError,
                                                                     CannotEditDeletedMessageError,
                                                                     NewTextCannotBeEmptyError, MessageIsTooLongError,
                                                                     DeletedMessageCannotBeMarkedAsReadError)
from LuminMessageService.app.domain.models.common.value_objects import MessageText


class Message(AggregateRoot):
    def __init__(
            self,
            message_id: UUID,
            sender_id: UUID,
            recipient_id: UUID,
            chat_id: UUID,
            text: MessageText,
            sent_at: datetime | None = None,
            read_at: datetime | None = None,
            edited_at: datetime | None = None,
    ) -> None:
        super().__init__(message_id)

        self._validate_creation(sender_id, recipient_id, chat_id, text)

        self._sender_id = sender_id
        self._recipient_id = recipient_id
        self._chat_id = chat_id
        self._text = text
        self._sent_at = sent_at or datetime.now()
        self._read_at = read_at
        self._edited_at = edited_at
        self._is_deleted = False

        self.add_domain_event(
            MessageSentEvent(
                aggregate_id=self.id,
                data={
                    'sender_id': str(self._sender_id),
                    'recipient_id': str(self._recipient_id),
                    'chat_id': str(self._chat_id),
                    'sent_at': self._sent_at.isoformat(),
                    'message_length': len(self._text.value)
                }
            )
        )

    @classmethod
    def create(cls, sender_id: UUID, recipient_id: UUID, chat_id: UUID, text: MessageText) -> "Message":
        return cls(
            message_id=uuid4(),
            sender_id=sender_id,
            recipient_id=recipient_id,
            chat_id=chat_id,
            text=text
        )

    @staticmethod
    def _validate_creation(sender_id: UUID, recipient_id: UUID,
                           chat_id: UUID, text: MessageText) -> None:
        if not sender_id:
            raise SenderIDCannotBeEmptyError("Sender ID cannot be empty")
        if not recipient_id:
            raise RecipientIDCannotBeEmptyError("Recipient ID cannot be empty")
        if not chat_id:
            raise ChatIDCannotBeEmptyError("Chat ID cannot be empty")
        if not text or not text.value.strip():
            raise MessageTextCannotBeEmptyError("Message text cannot be empty")
        if sender_id == recipient_id:
            raise CannotSendMessageToYourselfError("Cannot send message to yourself")

    def mark_as_read(self, read_at: datetime | None = None) -> None:
        if self._is_deleted:
            raise CannotReadDeletedMessageError("Cannot read deleted message")
        if self._read_at:
            return None

        self._read_at = read_at or datetime.now()
        self._increment_version()

        self.add_domain_event(
            MessageReadEvent(
                aggregate_id=self.id,
                data={'read_at': self._read_at.isoformat()}
            )
        )

    def edit_text(self, new_text: MessageText, edited_at: datetime | None = None) -> None:
        if self._is_deleted:
            raise CannotEditDeletedMessageError("Cannot edit deleted message")
        if not new_text or not new_text.value.strip():
            raise NewTextCannotBeEmptyError("New text cannot be empty")
        if len(new_text.value) > 5000:
            raise MessageIsTooLongError("Message is too long")

        old_text = self._text
        self._text = new_text
        self._edited_at = edited_at or datetime.now()
        self._increment_version()

        self.add_domain_event(
            MessageEditedEvent(
                aggregate_id=self.id,
                data={
                    'old_text': old_text,
                    'new_text': self._text.value,
                    'edited_at': self._edited_at.isoformat()
                }
            )
        )

    def delete(self) -> None:
        if self._is_deleted:
            return

        self._is_deleted = True
        self._increment_version()

    @property
    def sender_id(self) -> UUID:
        return self._sender_id

    @property
    def recipient_id(self) -> UUID:
        return self._recipient_id

    @property
    def chat_id(self) -> UUID:
        return self._chat_id

    @property
    def text(self) -> MessageText:
        return self._text

    @property
    def sent_at(self) -> datetime:
        return self._sent_at

    @property
    def read_at(self) -> datetime | None:
        return self._read_at

    @property
    def edited_at(self) -> datetime | None:
        return self._edited_at

    @property
    def is_read(self) -> bool:
        return self._read_at is not None

    @property
    def is_edited(self) -> bool:
        return self._edited_at is not None

    @property
    def is_deleted(self) -> bool:
        return self._is_deleted

    def validate_invariants(self) -> None:
        if not self._text or not self._text.value.strip():
            raise MessageTextCannotBeEmptyError("Message text cannot be empty")
        if not self._sender_id:
            raise SenderIDCannotBeEmptyError("Sender ID cannot be empty")
        if not self._recipient_id:
            raise RecipientIDCannotBeEmptyError("Recipient ID cannot be empty")
        if self._is_deleted and self._read_at:
            raise DeletedMessageCannotBeMarkedAsReadError("Deleted message cannot be marked as read")
