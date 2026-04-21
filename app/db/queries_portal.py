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


DEFAULT_OFFERS = [
    {
        "title": "Bike Repair",
        "description": "We fix your bike.",
        "availability": "Mondays, Wednesdays and Fridays from 16:00",
        "extra": "Home service",
        "price": 10,
        "image_key": "bike",
        "owner_name": "Carlos Gomez",
    },
    {
        "title": "English Lessons",
        "description": "Practice English with a native speaker.",
        "availability": "Weekdays from 18:00",
        "extra": "Online",
        "price": 8,
        "image_key": "ingles",
        "owner_name": "Laura Perez",
    },
    {
        "title": "House Cleaning",
        "description": "I help you keep your house clean.",
        "availability": "Weekends",
        "extra": "At your place",
        "price": 12,
        "image_key": "clean",
        "owner_name": "Marina Lopez",
    },
    {
        "title": "Dog Walking",
        "description": "I take care of your dog.",
        "availability": "Every afternoon",
        "extra": "Outdoor service",
        "price": 6,
        "image_key": "dog",
        "owner_name": "Lucia Martin",
    },
    {
        "title": "Math Tutoring",
        "description": "Help with school math subjects.",
        "availability": "Evenings",
        "extra": "Online or in person",
        "price": 9,
        "image_key": "mates",
        "owner_name": "David Ruiz",
    },
    {
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
        "address": "Calle Calatrava Nº2",
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
        "address": "Calle Toledo Nº5",
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


def seed_default_service_offers(db: Session) -> None:
    if db.query(ServiceOffer).count() > 0:
        return

    db.add_all(ServiceOffer(**offer) for offer in DEFAULT_OFFERS)
    db.commit()


def ensure_user_portal_seed_data(db: Session, user: User) -> None:
    wallet = db.query(UserWallet).filter(UserWallet.user_id == user.id).first()
    if wallet is None:
        wallet = UserWallet(user_id=user.id, balance=42, status="Active")
        db.add(wallet)
        db.flush()
        db.add_all(
            WalletRecharge(user_id=user.id, amount=item["amount"], created_at=item["created_at"])
            for item in DEFAULT_RECHARGES
        )

    if db.query(ServiceRequest).filter(ServiceRequest.receiver_id == user.id).count() == 0:
        db.add_all(ServiceRequest(receiver_id=user.id, **item) for item in DEFAULT_REQUESTS)

    if db.query(UserTransaction).filter(UserTransaction.user_id == user.id).count() == 0:
        db.add_all(UserTransaction(user_id=user.id, **item) for item in DEFAULT_TRANSACTIONS)

    db.commit()


def list_service_offers(db: Session) -> list[ServiceOffer]:
    return db.query(ServiceOffer).order_by(ServiceOffer.id.asc()).all()


def list_user_transactions(db: Session, user_id: int) -> list[UserTransaction]:
    return (
        db.query(UserTransaction)
        .filter(UserTransaction.user_id == user_id)
        .order_by(UserTransaction.occurred_at.desc(), UserTransaction.id.desc())
        .all()
    )


def list_received_requests(db: Session, user_id: int) -> list[ServiceRequest]:
    return (
        db.query(ServiceRequest)
        .filter(ServiceRequest.receiver_id == user_id)
        .order_by(ServiceRequest.created_at.desc(), ServiceRequest.id.desc())
        .all()
    )


def get_request_for_receiver(db: Session, request_id: int, receiver_id: int) -> ServiceRequest | None:
    return (
        db.query(ServiceRequest)
        .filter(ServiceRequest.id == request_id, ServiceRequest.receiver_id == receiver_id)
        .first()
    )


def accept_request(db: Session, request_row: ServiceRequest, clarification: str) -> ServiceRequest:
    request_row.status = "accepted"
    request_row.clarification = clarification or None
    request_row.reject_reason = None
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
    db.commit()
    db.refresh(request_row)
    return request_row


def get_or_create_wallet(db: Session, user_id: int) -> UserWallet:
    wallet = db.query(UserWallet).filter(UserWallet.user_id == user_id).first()
    if wallet is None:
        wallet = UserWallet(user_id=user_id, balance=42, status="Active")
        db.add(wallet)
        db.commit()
        db.refresh(wallet)
    return wallet


def list_wallet_recharges(db: Session, user_id: int) -> list[WalletRecharge]:
    return (
        db.query(WalletRecharge)
        .filter(WalletRecharge.user_id == user_id)
        .order_by(WalletRecharge.created_at.desc(), WalletRecharge.id.desc())
        .all()
    )


def create_wallet_recharge(db: Session, user_id: int, amount: int) -> UserWallet:
    wallet = get_or_create_wallet(db, user_id)
    wallet.balance += amount
    db.add(WalletRecharge(user_id=user_id, amount=amount))
    db.commit()
    db.refresh(wallet)
    return wallet
