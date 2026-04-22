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


DEFAULT_OFFERS = [
    {
        "owner_id": None,
        "title": "Bike Repair",
        "description": "We fix your bike.",
        "availability": "Mondays, Wednesdays and Fridays from 16:00",
        "extra": "Home service",
        "price": 10,
        "image_key": "bike",
        "owner_name": "Carlos Gomez",
    },
    {
        "owner_id": None,
        "title": "English Lessons",
        "description": "Practice English with a native speaker.",
        "availability": "Weekdays from 18:00",
        "extra": "Online",
        "price": 8,
        "image_key": "ingles",
        "owner_name": "Laura Perez",
    },
    {
        "owner_id": None,
        "title": "House Cleaning",
        "description": "I help you keep your house clean.",
        "availability": "Weekends",
        "extra": "At your place",
        "price": 12,
        "image_key": "clean",
        "owner_name": "Marina Lopez",
    },
    {
        "owner_id": None,
        "title": "Dog Walking",
        "description": "I take care of your dog.",
        "availability": "Every afternoon",
        "extra": "Outdoor service",
        "price": 6,
        "image_key": "dog",
        "owner_name": "Lucia Martin",
    },
    {
        "owner_id": None,
        "title": "Math Tutoring",
        "description": "Help with school math subjects.",
        "availability": "Evenings",
        "extra": "Online or in person",
        "price": 9,
        "image_key": "mates",
        "owner_name": "David Ruiz",
    },
    {
        "owner_id": None,
        "title": "Computer Repair",
        "description": "Fix software and hardware issues.",
        "availability": "Flexible schedule",
        "extra": "Home service",
        "price": 15,
        "image_key": "computer",
        "owner_name": "Sergio Diaz",
    },
]


DEFAULT_REQUESTS = [
    {
        "requester_name": "Javier Ortega",
        "service": "Bike Repair",
        "description": "We fix your bike.",
        "scheduled_at": "Monday 14 at 16:00",
        "address": "Main Street No. 2",
        "message": "Doorbell is not working",
        "image_key": "bike",
        "price": 10,
        "status": "pending",
    },
    {
        "requester_name": "Paula Martin",
        "service": "House Cleaning",
        "description": "I clean your house.",
        "scheduled_at": "Wednesday 16 at 10:00",
        "address": "Toledo Street No. 5",
        "message": "Bring your own products",
        "image_key": "clean",
        "price": 12,
        "status": "pending",
    },
    {
        "requester_name": "Alberto Diaz",
        "service": "Dog Walking",
        "description": "I walk your dog.",
        "scheduled_at": "Friday 18 at 18:00",
        "address": "Central Park",
        "message": "Small dog, very friendly",
        "image_key": "dog",
        "price": 6,
        "status": "accepted",
        "clarification": "I will arrive 10 minutes early.",
    },
    {
        "requester_name": "Marta Suarez",
        "service": "Computer Repair",
        "description": "Fix your computer.",
        "scheduled_at": "Saturday 20 at 12:00",
        "address": "Online",
        "message": "Laptop not turning on",
        "image_key": "computer",
        "price": 15,
        "status": "rejected",
        "reject_reason": "I am not available at that time.",
    },
]


DEFAULT_TRANSACTIONS = [
    {
        "type": "Purchase",
        "service": "Bike Repair",
        "other_user": "Carlos Gomez",
        "amount": -10,
        "status": "Completed",
        "occurred_at": datetime(2026, 4, 12, 0, 0, 0),
    },
    {
        "type": "Sale",
        "service": "English Lessons",
        "other_user": "Laura Perez",
        "amount": 8,
        "status": "Completed",
        "occurred_at": datetime(2026, 4, 10, 0, 0, 0),
    },
    {
        "type": "Purchase",
        "service": "House Cleaning",
        "other_user": "Marina Lopez",
        "amount": -12,
        "status": "Pending",
        "occurred_at": datetime(2026, 4, 8, 0, 0, 0),
    },
    {
        "type": "Sale",
        "service": "Math Tutoring",
        "other_user": "David Ruiz",
        "amount": 9,
        "status": "Completed",
        "occurred_at": datetime(2026, 4, 5, 0, 0, 0),
    },
    {
        "type": "Purchase",
        "service": "Dog Walking",
        "other_user": "Lucia Martin",
        "amount": -6,
        "status": "Cancelled",
        "occurred_at": datetime(2026, 4, 3, 0, 0, 0),
    },
    {
        "type": "Sale",
        "service": "Computer Repair",
        "other_user": "Sergio Diaz",
        "amount": 15,
        "status": "Completed",
        "occurred_at": datetime(2026, 4, 1, 0, 0, 0),
    },
]


DEFAULT_RECHARGES = [
    {"amount": 20, "created_at": datetime(2026, 4, 18, 0, 0, 0)},
    {"amount": 15, "created_at": datetime(2026, 4, 10, 0, 0, 0)},
    {"amount": 10, "created_at": datetime(2026, 4, 3, 0, 0, 0)},
]


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

    for offer in DEFAULT_OFFERS:
        db.query(ServiceOffer).filter(
            ServiceOffer.title == offer["title"],
            ServiceOffer.description == offer["description"],
            ServiceOffer.availability == offer["availability"],
            ServiceOffer.extra == offer["extra"],
            ServiceOffer.price == offer["price"],
            ServiceOffer.image_key == offer["image_key"],
        ).delete(synchronize_session=False)

    # Legacy seeded requests were created without links to a real requester, offer, or transaction.
    # Removing them by structure is more reliable than matching exact text values.
    db.query(ServiceRequest).filter(
        ServiceRequest.requester_id.is_(None),
        ServiceRequest.service_offer_id.is_(None),
        ServiceRequest.buyer_transaction_id.is_(None),
    ).delete(synchronize_session=False)

    for transaction in DEFAULT_TRANSACTIONS:
        db.query(UserTransaction).filter(
            UserTransaction.type == transaction["type"],
            UserTransaction.service == transaction["service"],
            UserTransaction.other_user == transaction["other_user"],
            UserTransaction.amount == transaction["amount"],
            UserTransaction.status == transaction["status"],
            UserTransaction.occurred_at == transaction["occurred_at"],
        ).delete(synchronize_session=False)

    for recharge in DEFAULT_RECHARGES:
        db.query(WalletRecharge).filter(
            WalletRecharge.amount == recharge["amount"],
            WalletRecharge.created_at == recharge["created_at"],
        ).delete(synchronize_session=False)

    db.commit()


def list_service_offers(db: Session) -> list[ServiceOffer]:
    # Return the full catalog in a stable order.
    return db.query(ServiceOffer).order_by(ServiceOffer.id.asc()).all()


def list_available_service_offers(db: Session, user_id: int) -> list[ServiceOffer]:
    # Return only services the current user can purchase.
    return (
        db.query(ServiceOffer)
        .filter(ServiceOffer.owner_id.is_not(None), ServiceOffer.owner_id != user_id)
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
        extra=extra,
        price=price,
        image_key=image_key,
        owner_name=full_name or provider.email,
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

    # The requester pending purchase becomes completed.
    if request_row.buyer_transaction_id:
        requester_transaction = db.query(UserTransaction).filter(
            UserTransaction.id == request_row.buyer_transaction_id
        ).first()
        if requester_transaction is not None:
            requester_transaction.status = "Completed"

    # When accepted, the amount is transferred to the provider wallet.
    provider_wallet = get_wallet_by_user_id(db, request_row.receiver_id)
    if provider_wallet is not None:
        provider_wallet.balance += request_row.price

    db.add(
        UserTransaction(
            user_id=request_row.receiver_id,
            type="Sale",
            service=request_row.service,
            other_user=request_row.requester_name,
            amount=request_row.price,
            status="Completed",
            occurred_at=datetime.utcnow(),
        )
    )
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


def create_wallet_recharge(db: Session, user_id: int, amount: int) -> UserWallet:
    # Update the balance and persist the recharge as a wallet movement.
    wallet = get_wallet_by_user_id(db, user_id)
    if wallet is None:
        raise ValueError("Wallet not found")
    wallet.balance += amount
    db.add(WalletRecharge(user_id=user_id, amount=amount))
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
