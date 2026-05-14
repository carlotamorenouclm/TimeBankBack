"""
Encapsula consultas y acceso a base de datos para mantener limpias las rutas.

Comentarios generados para documentar la intencion de cada bloque principal.
"""
# Queries for chat messages linked to service requests.
from sqlalchemy.orm import Session

from app.models.chat import ChatMessage
from app.models.portal import ServiceRequest, UserTransaction
from app.models.users import User


LEGACY_DEMO_USER_EMAILS = ["seller.demo@timebank.local"]


# Encapsula una parte concreta de la logica de la aplicacion.
def cleanup_chat_for_seeded_portal_data(db: Session) -> None:
    demo_users = db.query(User).filter(User.email.in_(LEGACY_DEMO_USER_EMAILS)).all()
    demo_user_ids = [user.id for user in demo_users]

    request_filters = []
    if demo_user_ids:
        request_filters.append(
            (ServiceRequest.receiver_id.in_(demo_user_ids))
            | (ServiceRequest.requester_id.in_(demo_user_ids))
        )
    request_filters.append(
        ServiceRequest.requester_id.is_(None)
        & ServiceRequest.service_offer_id.is_(None)
        & ServiceRequest.buyer_transaction_id.is_(None)
    )

    request_ids = []
    for request_filter in request_filters:
        request_ids.extend(
            request.id
            for request in db.query(ServiceRequest.id).filter(request_filter).all()
        )

    if request_ids:
        db.query(ChatMessage).filter(
            ChatMessage.service_request_id.in_(set(request_ids))
        ).delete(synchronize_session=False)


# Recupera la informacion solicitada desde la capa correspondiente.
def get_request_by_history_transaction_id(
    db: Session,
    transaction_id: int,
) -> ServiceRequest | None:
    request_row = (
        db.query(ServiceRequest)
        .filter(
            (ServiceRequest.buyer_transaction_id == transaction_id)
            | (ServiceRequest.seller_transaction_id == transaction_id)
        )
        .first()
    )
    if request_row is not None:
        return request_row

    transaction = db.query(UserTransaction).filter(UserTransaction.id == transaction_id).first()
    if transaction is None or transaction.type != "Sale":
        return None

    return (
        db.query(ServiceRequest)
        .filter(
            ServiceRequest.receiver_id == transaction.user_id,
            ServiceRequest.service == transaction.service,
            ServiceRequest.requester_name == transaction.other_user,
            ServiceRequest.price == transaction.amount,
            ServiceRequest.status.in_(["accepted", "completed"]),
        )
        .order_by(ServiceRequest.created_at.desc(), ServiceRequest.id.desc())
        .first()
    )


# Encapsula una parte concreta de la logica de la aplicacion.
def _user_display_name(user: User) -> str:
    full_name = " ".join(part for part in [user.name, user.surname] if part).strip()
    return full_name or user.email


# Recupera la informacion solicitada desde la capa correspondiente.
def get_user_by_display_name(db: Session, display_name: str | None) -> User | None:
    if not display_name:
        return None

    for user in db.query(User).all():
        if _user_display_name(user) == display_name:
            return user
    return None


# Recupera la informacion solicitada desde la capa correspondiente.
def get_history_chat_info(db: Session, transaction: UserTransaction) -> tuple[str | None, int | None]:
    linked_request = get_request_by_history_transaction_id(db, transaction.id)
    if linked_request is not None:
        other_user_id = (
            linked_request.receiver_id
            if linked_request.requester_id == transaction.user_id
            else linked_request.requester_id
        )
        return f"request-{linked_request.id}", other_user_id

    current_user = db.query(User).filter(User.id == transaction.user_id).first()
    other_user = get_user_by_display_name(db, transaction.other_user)
    if current_user is None or other_user is None:
        return f"transaction-{transaction.id}", other_user.id if other_user is not None else None

    counterpart = (
        db.query(UserTransaction)
        .filter(
            UserTransaction.user_id == other_user.id,
            UserTransaction.service == transaction.service,
            UserTransaction.other_user == _user_display_name(current_user),
            UserTransaction.amount == -transaction.amount,
            UserTransaction.status == transaction.status,
        )
        .order_by(UserTransaction.id.asc())
        .all()
    )

    if counterpart:
        closest = min(
            counterpart,
            key=lambda item: abs((item.occurred_at - transaction.occurred_at).total_seconds()),
        )
        first_id, second_id = sorted([transaction.id, closest.id])
        return f"transaction-{first_id}-{second_id}", other_user.id

    return f"transaction-{transaction.id}", other_user.id


# Recupera la informacion solicitada desde la capa correspondiente.
def get_request_for_chat(db: Session, request_id: int, user_id: int) -> ServiceRequest | None:
    return (
        db.query(ServiceRequest)
        .filter(
            ServiceRequest.id == request_id,
            (ServiceRequest.requester_id == user_id) | (ServiceRequest.receiver_id == user_id),
        )
        .first()
    )


# Recupera la informacion solicitada desde la capa correspondiente.
def list_chat_messages(db: Session, request_id: int) -> list[ChatMessage]:
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.service_request_id == request_id)
        .order_by(ChatMessage.created_at.asc(), ChatMessage.id.asc())
        .all()
    )


# Encapsula una parte concreta de la logica de la aplicacion.
def count_unread_request_messages(db: Session, request_id: int, user_id: int) -> int:
    return (
        db.query(ChatMessage)
        .filter(
            ChatMessage.service_request_id == request_id,
            ChatMessage.receiver_id == user_id,
            ChatMessage.is_read.is_(False),
        )
        .count()
    )


# Encapsula una parte concreta de la logica de la aplicacion.
def mark_request_messages_read(db: Session, request_id: int, user_id: int) -> None:
    db.query(ChatMessage).filter(
        ChatMessage.service_request_id == request_id,
        ChatMessage.receiver_id == user_id,
        ChatMessage.is_read.is_(False),
    ).update({ChatMessage.is_read: True}, synchronize_session=False)
    db.commit()


# Recupera la informacion solicitada desde la capa correspondiente.
def list_thread_messages(db: Session, thread_key: str) -> list[ChatMessage]:
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.thread_key == thread_key)
        .order_by(ChatMessage.created_at.asc(), ChatMessage.id.asc())
        .all()
    )


# Encapsula una parte concreta de la logica de la aplicacion.
def count_unread_thread_messages(db: Session, thread_key: str, user_id: int) -> int:
    return (
        db.query(ChatMessage)
        .filter(
            ChatMessage.thread_key == thread_key,
            ChatMessage.receiver_id == user_id,
            ChatMessage.is_read.is_(False),
        )
        .count()
    )


# Encapsula una parte concreta de la logica de la aplicacion.
def mark_thread_messages_read(db: Session, thread_key: str, user_id: int) -> None:
    db.query(ChatMessage).filter(
        ChatMessage.thread_key == thread_key,
        ChatMessage.receiver_id == user_id,
        ChatMessage.is_read.is_(False),
    ).update({ChatMessage.is_read: True}, synchronize_session=False)
    db.commit()


# Crea o registra el recurso solicitado y prepara la respuesta.
def create_chat_message(
    db: Session,
    request_row: ServiceRequest,
    sender_id: int,
    message: str,
) -> ChatMessage:
    receiver_id = (
        request_row.receiver_id
        if request_row.requester_id == sender_id
        else request_row.requester_id
    )
    if receiver_id is None:
        raise ValueError("Receiver not found")

    chat_message = ChatMessage(
        service_request_id=request_row.id,
        thread_key=f"request-{request_row.id}",
        sender_id=sender_id,
        receiver_id=receiver_id,
        message=message.strip(),
    )
    db.add(chat_message)
    db.commit()
    db.refresh(chat_message)
    return chat_message


# Crea o registra el recurso solicitado y prepara la respuesta.
def create_thread_message(
    db: Session,
    thread_key: str,
    sender_id: int,
    receiver_id: int,
    message: str,
) -> ChatMessage:
    chat_message = ChatMessage(
        thread_key=thread_key,
        sender_id=sender_id,
        receiver_id=receiver_id,
        message=message.strip(),
    )
    db.add(chat_message)
    db.commit()
    db.refresh(chat_message)
    return chat_message
