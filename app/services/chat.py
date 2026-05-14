"""
Contiene logica de negocio reutilizable entre rutas y consultas.

Comentarios generados para documentar la intencion de cada bloque principal.
"""
# Service layer for request chats.
from sqlalchemy.orm import Session

from app.db.queries_chat import (
    create_chat_message,
    create_thread_message,
    get_request_for_chat,
    list_chat_messages,
    list_thread_messages,
    mark_request_messages_read,
    mark_thread_messages_read,
)
from app.db.queries_users import get_user_by_id
from app.schemas.chat import ChatMessageOut, ChatMessagesResponse
from app.schemas.portal import format_datetime


# Define esta clase y agrupa los datos que pertenecen a la entidad.
class ChatNotFoundError(Exception):
    pass


# Encapsula una parte concreta de la logica de la aplicacion.
def _sender_name(db: Session, sender_id: int) -> str:
    sender = get_user_by_id(db, sender_id)
    if sender is None:
        return "Unknown user"
    full_name = " ".join(part for part in [sender.name, sender.surname] if part).strip()
    return full_name or sender.email


# Encapsula una parte concreta de la logica de la aplicacion.
def _build_chat_response(db: Session, request_id: int, user_id: int) -> ChatMessagesResponse:
    messages = [
        ChatMessageOut(
            id=item.id,
            message=item.message,
            sender_id=item.sender_id,
            receiver_id=item.receiver_id,
            sender_name=_sender_name(db, item.sender_id),
            sent_at=format_datetime(item.created_at),
            is_mine=item.sender_id == user_id,
        )
        for item in list_chat_messages(db, request_id)
    ]
    return ChatMessagesResponse(messages=messages)


# Recupera la informacion solicitada desde la capa correspondiente.
def get_chat_messages_response(db: Session, request_id: int, user_id: int) -> ChatMessagesResponse:
    request_row = get_request_for_chat(db, request_id, user_id)
    if request_row is None:
        raise ChatNotFoundError("Chat not found")
    mark_request_messages_read(db, request_id, user_id)
    return _build_chat_response(db, request_id, user_id)


# Encapsula una parte concreta de la logica de la aplicacion.
def send_chat_message_response(
    db: Session,
    request_id: int,
    user_id: int,
    message: str,
) -> ChatMessagesResponse:
    request_row = get_request_for_chat(db, request_id, user_id)
    if request_row is None:
        raise ChatNotFoundError("Chat not found")

    try:
        create_chat_message(db, request_row, user_id, message)
    except ValueError as exc:
        raise ChatNotFoundError(str(exc)) from exc

    return _build_chat_response(db, request_id, user_id)


# Recupera la informacion solicitada desde la capa correspondiente.
def get_thread_messages_response(db: Session, thread_key: str, user_id: int) -> ChatMessagesResponse:
    mark_thread_messages_read(db, thread_key, user_id)
    messages = [
        ChatMessageOut(
            id=item.id,
            message=item.message,
            sender_id=item.sender_id,
            receiver_id=item.receiver_id,
            sender_name=_sender_name(db, item.sender_id),
            sent_at=format_datetime(item.created_at),
            is_mine=item.sender_id == user_id,
        )
        for item in list_thread_messages(db, thread_key)
        if item.sender_id == user_id or item.receiver_id == user_id
    ]
    return ChatMessagesResponse(messages=messages)


# Encapsula una parte concreta de la logica de la aplicacion.
def send_thread_message_response(
    db: Session,
    thread_key: str,
    user_id: int,
    receiver_id: int | None,
    message: str,
) -> ChatMessagesResponse:
    if receiver_id is None:
        raise ChatNotFoundError("Receiver not found")

    create_thread_message(db, thread_key, user_id, receiver_id, message)
    return get_thread_messages_response(db, thread_key, user_id)
