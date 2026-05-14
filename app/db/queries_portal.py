# Portal queries plus cleanup helpers for catalog, inbox, wallet, and history.
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.portal import (
    ServiceOffer,
    ServiceRequest,
    UserTransaction,
    UserWallet,
    WalletRecharge,
)
from app.models.users import User


LEGACY_DEMO_USER_EMAILS = ["seller.demo@timebank.local"]


def ensure_user_portal_data(db: Session, user: User) -> None:
    # Keep only the wallet bootstrap for new users, without fake requests or history.
    wallet = db.query(UserWallet).filter(UserWallet.user_id == user.id).first()
    if wallet is None:
        wallet = UserWallet(user_id=user.id, balance=0, status="Active")
        db.add(wallet)
    db.commit()


def cleanup_seeded_portal_data(db: Session) -> None:
    # Remove old demo records so only real database content remains visible.
    demo_users = db.query(User).filter(User.email.in_(LEGACY_DEMO_USER_EMAILS)).all()
    demo_user_ids = [user.id for user in demo_users]

    if demo_user_ids:
        db.query(ServiceRequest).filter(
            (ServiceRequest.receiver_id.in_(demo_user_ids))
            | (ServiceRequest.requester_id.in_(demo_user_ids))
        ).delete(synchronize_session=False)
        db.query(UserTransaction).filter(
            UserTransaction.user_id.in_(demo_user_ids)
        ).delete(synchronize_session=False)
        db.query(WalletRecharge).filter(
            WalletRecharge.user_id.in_(demo_user_ids)
        ).delete(synchronize_session=False)
        db.query(UserWallet).filter(UserWallet.user_id.in_(demo_user_ids)).delete(
            synchronize_session=False
        )
        db.query(ServiceOffer).filter(ServiceOffer.owner_id.in_(demo_user_ids)).delete(
            synchronize_session=False
        )
        db.query(User).filter(User.id.in_(demo_user_ids)).delete(synchronize_session=False)


    # Legacy seeded requests were created without links to a real requester, offer, or transaction.
    # Removing them by structure is more reliable than matching exact text values.
    db.query(ServiceRequest).filter(
        ServiceRequest.requester_id.is_(None),
        ServiceRequest.service_offer_id.is_(None),
        ServiceRequest.buyer_transaction_id.is_(None),
    ).delete(synchronize_session=False)


def list_service_offers(db: Session) -> list[ServiceOffer]:
    # Return the full catalog in a stable order.
    return db.query(ServiceOffer).order_by(ServiceOffer.id.asc()).all()


def list_available_service_offers(db: Session, user_id: int) -> list[ServiceOffer]:
    # Return only services the current user can purchase.
    return (
        db.query(ServiceOffer)
        .filter(
            ServiceOffer.owner_id.is_not(None),
            ServiceOffer.owner_id != user_id,
            ServiceOffer.is_visible.is_(True),
        )
        .order_by(ServiceOffer.id.asc())
        .all()
    )


def list_owned_service_offers(db: Session, user_id: int) -> list[ServiceOffer]:
    # Return only the services published by the current user.
    return (
        db.query(ServiceOffer)
        .filter(ServiceOffer.owner_id == user_id)
        .order_by(ServiceOffer.id.asc())
        .all()
    )


def get_service_offer_by_id(db: Session, service_offer_id: int) -> ServiceOffer | None:
    return db.query(ServiceOffer).filter(ServiceOffer.id == service_offer_id).first()


def delete_service_offer(db: Session, service_offer: ServiceOffer) -> int:
    # Delete a service publication only when it is not referenced by any request.
    linked_requests = (
        db.query(ServiceRequest)
        .filter(ServiceRequest.service_offer_id == service_offer.id)
        .count()
    )
    if linked_requests > 0:
        raise ValueError("You cannot delete a service that already has requests")

    deleted_service_id = service_offer.id
    db.delete(service_offer)
    db.commit()
    return deleted_service_id


def create_service_offer(
    db: Session,
    provider: User,
    title: str,
    description: str,
    availability: str,
    home_service: bool,
    address: str | None,
    extra: str | None,
    price: int,
    image_key: str,
) -> ServiceOffer:
    # Persist a new catalog service owned by the authenticated provider.
    full_name = " ".join(part for part in [provider.name, provider.surname] if part).strip()

    service_offer = ServiceOffer(
        owner_id=provider.id,
        title=title,
        description=description,
        availability=availability,
        home_service=home_service,
        address=address,
        extra=extra,
        price=price,
        image_key=image_key,
        owner_name=full_name or provider.email,
        is_visible=True,
    )
    db.add(service_offer)
    db.commit()
    db.refresh(service_offer)
    return service_offer


def list_user_transactions(db: Session, user_id: int) -> list[UserTransaction]:
    return (
        db.query(UserTransaction)
        .filter(UserTransaction.user_id == user_id)
        .order_by(UserTransaction.occurred_at.desc(), UserTransaction.id.desc())
        .all()
    )


def mark_user_transaction_updates_seen(db: Session, user_id: int, transaction_type: str) -> None:
    db.query(UserTransaction).filter(
        UserTransaction.user_id == user_id,
        UserTransaction.type == transaction_type,
        UserTransaction.has_unseen_update.is_(True),
    ).update({UserTransaction.has_unseen_update: False}, synchronize_session=False)
    db.commit()


def mark_transaction_update_unseen(db: Session, transaction_id: int | None) -> None:
    if transaction_id is None:
        return

    db.query(UserTransaction).filter(
        UserTransaction.id == transaction_id,
    ).update({UserTransaction.has_unseen_update: True}, synchronize_session=False)
    db.commit()


def mark_request_transaction_update_seen(
    db: Session,
    request_row: ServiceRequest,
    user_id: int,
) -> None:
    transaction_id = None
    if request_row.requester_id == user_id:
        transaction_id = request_row.buyer_transaction_id
    elif request_row.receiver_id == user_id:
        transaction_id = request_row.seller_transaction_id

    if transaction_id is None:
        return

    db.query(UserTransaction).filter(
        UserTransaction.id == transaction_id,
        UserTransaction.user_id == user_id,
    ).update({UserTransaction.has_unseen_update: False}, synchronize_session=False)
    db.commit()


def get_transaction_by_id(db: Session, transaction_id: int) -> UserTransaction | None:
    return db.query(UserTransaction).filter(UserTransaction.id == transaction_id).first()


def get_request_by_transaction_id(db: Session, transaction_id: int) -> ServiceRequest | None:
    # Link a buyer history movement with its original service request when it exists.
    return (
        db.query(ServiceRequest)
        .filter(ServiceRequest.buyer_transaction_id == transaction_id)
        .first()
    )


def list_received_requests(db: Session, user_id: int) -> list[ServiceRequest]:
    return (
        db.query(ServiceRequest)
        .filter(ServiceRequest.receiver_id == user_id)
        .order_by(ServiceRequest.created_at.desc(), ServiceRequest.id.desc())
        .all()
    )


def count_pending_received_requests(db: Session, user_id: int) -> int:
    return (
        db.query(ServiceRequest)
        .filter(ServiceRequest.receiver_id == user_id, ServiceRequest.status == "pending")
        .count()
    )


def get_request_for_receiver(db: Session, request_id: int, receiver_id: int) -> ServiceRequest | None:
    # Ensure only requests owned by the authenticated receiver can be changed.
    return (
        db.query(ServiceRequest)
        .filter(ServiceRequest.id == request_id, ServiceRequest.receiver_id == receiver_id)
        .first()
    )


def accept_request(db: Session, request_row: ServiceRequest, clarification: str) -> ServiceRequest:
    # Accepting a request also finalizes the related history transaction.
    request_row.status = "accepted"
    request_row.clarification = clarification or None
    request_row.reject_reason = None

    # The requester pending purchase becomes accepted.
    if request_row.buyer_transaction_id:
        requester_transaction = db.query(UserTransaction).filter(
            UserTransaction.id == request_row.buyer_transaction_id
        ).first()
        if requester_transaction is not None:
            requester_transaction.status = "Accepted"
            requester_transaction.has_unseen_update = True

    provider_transaction = UserTransaction(
        user_id=request_row.receiver_id,
        type="Sale",
        service=request_row.service,
        other_user=request_row.requester_name,
        amount=request_row.price,
        status="Accepted",
        occurred_at=datetime.utcnow(),
    )
    db.add(provider_transaction)
    db.flush()
    request_row.seller_transaction_id = provider_transaction.id

    db.commit()
    db.refresh(request_row)
    return request_row


def reject_request(db: Session, request_row: ServiceRequest, reason: str) -> ServiceRequest:
    request_row.status = "rejected"
    request_row.reject_reason = reason
    request_row.clarification = None

    # If the request is rejected, refund the requester automatically.
    if request_row.requester_id:
        requester_wallet = get_wallet_by_user_id(db, request_row.requester_id)
        if requester_wallet is not None:
            requester_wallet.balance += request_row.price

    if request_row.buyer_transaction_id:
        requester_transaction = db.query(UserTransaction).filter(
            UserTransaction.id == request_row.buyer_transaction_id
        ).first()
        if requester_transaction is not None:
            requester_transaction.status = "Cancelled"
            requester_transaction.has_unseen_update = True

    provider_transaction = UserTransaction(
        user_id=request_row.receiver_id,
        type="Sale",
        service=request_row.service,
        other_user=request_row.requester_name,
        amount=0,
        status="Rejected",
        occurred_at=datetime.utcnow(),
    )
    db.add(provider_transaction)
    db.flush()
    request_row.seller_transaction_id = provider_transaction.id

    db.commit()
    db.refresh(request_row)
    return request_row


def get_request_for_user(db: Session, request_id: int, user_id: int) -> ServiceRequest | None:
    return (
        db.query(ServiceRequest)
        .filter(
            ServiceRequest.id == request_id,
            (ServiceRequest.requester_id == user_id) | (ServiceRequest.receiver_id == user_id),
        )
        .first()
    )


def complete_request(db: Session, request_row: ServiceRequest) -> ServiceRequest:
    if request_row.status != "accepted":
        raise ValueError("Only accepted requests can be completed")

    request_row.status = "completed"

    if request_row.buyer_transaction_id:
        buyer_transaction = db.query(UserTransaction).filter(
            UserTransaction.id == request_row.buyer_transaction_id
        ).first()
        if buyer_transaction is not None:
            buyer_transaction.status = "Completed"
            buyer_transaction.has_unseen_update = True

    if request_row.seller_transaction_id:
        seller_transaction = db.query(UserTransaction).filter(
            UserTransaction.id == request_row.seller_transaction_id
        ).first()
        if seller_transaction is not None:
            seller_transaction.status = "Completed"
            seller_transaction.has_unseen_update = True

    # Transfer funds to the provider wallet once the service is completed.
    provider_wallet = get_wallet_by_user_id(db, request_row.receiver_id)
    if provider_wallet is not None:
        provider_wallet.balance += request_row.price

    db.commit()
    db.refresh(request_row)
    return request_row


def get_wallet_by_user_id(db: Session, user_id: int) -> UserWallet | None:
    return db.query(UserWallet).filter(UserWallet.user_id == user_id).first()


def list_wallet_recharges(db: Session, user_id: int) -> list[WalletRecharge]:
    return (
        db.query(WalletRecharge)
        .filter(WalletRecharge.user_id == user_id)
        .order_by(WalletRecharge.created_at.desc(), WalletRecharge.id.desc())
        .all()
    )


def create_wallet_recharge(
    db: Session,
    user_id: int,
    amount: int,
    stripe_checkout_session_id: str | None = None,
) -> UserWallet:
    # Update the balance and persist the recharge as a wallet movement.
    wallet = get_wallet_by_user_id(db, user_id)
    if wallet is None:
        raise ValueError("Wallet not found")

    if stripe_checkout_session_id:
        existing_recharge = db.query(WalletRecharge).filter(
            WalletRecharge.stripe_checkout_session_id == stripe_checkout_session_id
        ).first()
        if existing_recharge is not None:
            return wallet

    wallet.balance += amount
    db.add(
        WalletRecharge(
            user_id=user_id,
            amount=amount,
            stripe_checkout_session_id=stripe_checkout_session_id,
        )
    )
    db.commit()
    db.refresh(wallet)
    return wallet


def create_purchase_request(
    db: Session,
    requester: User,
    service_offer: ServiceOffer,
    scheduled_at: str,
    address: str,
    message: str | None = None,
) -> ServiceRequest:
    # Create a real purchase request and hold the money in the requester wallet.
    if service_offer.owner_id is None:
        raise ValueError("Service provider not found")

    if service_offer.owner_id == requester.id:
        raise ValueError("You cannot request your own service")

    requester_wallet = get_wallet_by_user_id(db, requester.id)
    if requester_wallet is None:
        raise ValueError("Wallet not found")

    if requester_wallet.balance < service_offer.price:
        raise ValueError("Insufficient balance")

    requester_wallet.balance -= service_offer.price

    full_name = " ".join(part for part in [requester.name, requester.surname] if part).strip()
    requester_name = full_name or requester.email

    requester_transaction = UserTransaction(
        user_id=requester.id,
        type="Purchase",
        service=service_offer.title,
        other_user=service_offer.owner_name,
        amount=-service_offer.price,
        status="Pending",
        occurred_at=datetime.utcnow(),
    )
    db.add(requester_transaction)
    db.flush()

    service_request = ServiceRequest(
        receiver_id=service_offer.owner_id,
        requester_id=requester.id,
        service_offer_id=service_offer.id,
        buyer_transaction_id=requester_transaction.id,
        requester_name=requester_name,
        service=service_offer.title,
        description=service_offer.description,
        scheduled_at=scheduled_at,
        address=address,
        message=message,
        image_key=service_offer.image_key,
        price=service_offer.price,
        status="pending",
    )
    db.add(service_request)
    db.commit()
    db.refresh(service_request)
    return service_request
