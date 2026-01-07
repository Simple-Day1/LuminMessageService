import uuid
from sqlalchemy import Column, UUID, String, Date, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class MessageModel(Base):
    __tablename__ = "messages"

    message_id = Column(UUID(), primary_key=True, default=lambda: uuid.uuid4())
    sender_id = Column(UUID(), primary_key=True, default=lambda: uuid.uuid4())
    recipient_id = Column(UUID(), primary_key=True, default=lambda: uuid.uuid4())
    chat_id = Column(UUID(), primary_key=True, default=lambda: uuid.uuid4())
    text = Column(String(300)),
    sent_at = Column(Date),
    read_at = Column(Date),
    edited_at = Column(Date),
    version = Column(Integer())
