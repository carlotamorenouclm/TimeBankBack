# Chat routes for messages between requester and provider.
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.session import get_db
from app.schemas.chat import ChatMessagesResponse, SendChatMessagePayload
from app.services.chat import (
    ChatNotFoundError,
    get_chat_messages_response,
    get_thread_messages_response,
    send_chat_message_response,
    send_thread_message_response,
)

router = APIRouter()


@router.get(
    "/requests/{request_id}/messages",
    response_model=ChatMessagesResponse,
    status_code=status.HTTP_200_OK,
)
def get_chat_messages(
    request_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        return get_chat_messages_response(db, request_id, current_user.id)
    except ChatNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post(
    "/requests/{request_id}/messages",
    response_model=ChatMessagesResponse,
    status_code=status.HTTP_201_CREATED,
)
def send_chat_message(
    request_id: int,
    payload: SendChatMessagePayload,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        return send_chat_message_response(db, request_id, current_user.id, payload.message)
    except ChatNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get(
    "/threads/{thread_key}/messages",
    response_model=ChatMessagesResponse,
    status_code=status.HTTP_200_OK,
)
def get_thread_messages(
    thread_key: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_thread_messages_response(db, thread_key, current_user.id)


@router.post(
    "/threads/{thread_key}/messages",
    response_model=ChatMessagesResponse,
    status_code=status.HTTP_201_CREATED,
)
def send_thread_message(
    thread_key: str,
    payload: SendChatMessagePayload,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        return send_thread_message_response(
            db,
            thread_key,
            current_user.id,
            payload.receiver_id,
            payload.message,
        )
    except ChatNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
