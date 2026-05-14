"""
Define esquemas Pydantic para validar entradas y serializar respuestas.

Comentarios generados para documentar la intencion de cada bloque principal.
"""
# Pydantic DTOs for request chats.
from pydantic import BaseModel, Field


# Define esta clase y agrupa los datos que pertenecen a la entidad.
class ChatMessageOut(BaseModel):
    id: int
    message: str
    sender_id: int
    receiver_id: int
    sender_name: str
    sent_at: str
    is_mine: bool


# Define esta clase y agrupa los datos que pertenecen a la entidad.
class ChatMessagesResponse(BaseModel):
    messages: list[ChatMessageOut]


# Define esta clase y agrupa los datos que pertenecen a la entidad.
class SendChatMessagePayload(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    receiver_id: int | None = None
