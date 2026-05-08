# Pydantic DTOs for request chats.
from pydantic import BaseModel, Field


class ChatMessageOut(BaseModel):
    id: int
    message: str
    sender_id: int
    receiver_id: int
    sender_name: str
    sent_at: str
    is_mine: bool


class ChatMessagesResponse(BaseModel):
    messages: list[ChatMessageOut]


class SendChatMessagePayload(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    receiver_id: int | None = None
