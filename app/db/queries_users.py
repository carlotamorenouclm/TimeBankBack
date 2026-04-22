# Consultas de usuario reutilizadas por registro, admin y autenticacion.
from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.portal import ServiceOffer, ServiceRequest, UserTransaction, UserWallet, WalletRecharge
from app.models.users import User
from app.core.security import hash_password
from app.db.queries_portal import ensure_user_portal_data


def add_user(
    db: Session,
    email: str,
    password: str,
    name: Optional[str] = None,
    surname: Optional[str] = None,
    avatar_key: Optional[str] = None,
) -> User:
    # Create the user and bootstrap only the minimum portal data.
    hashed = hash_password(password)
    user = User(
        email=email,
        hashed_password=hashed,
        name=name,
        surname=surname,
        avatar_key=avatar_key,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    ensure_user_portal_data(db, user)
    return user


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def list_users(db: Session) -> List[User]:
    return db.query(User).filter(User.role == "USER").order_by(User.id.asc()).all()


def delete_user(db: Session, user_id: int) -> bool:
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    return delete_user_account(db, user)


def delete_user_account(db: Session, user: User) -> bool:
    # Remove dependent portal records before deleting the user account itself.
    owned_service_ids = [
        service.id
        for service in db.query(ServiceOffer.id).filter(ServiceOffer.owner_id == user.id).all()
    ]

    if owned_service_ids:
        db.query(ServiceRequest).filter(
            ServiceRequest.service_offer_id.in_(owned_service_ids)
        ).delete(synchronize_session=False)

    db.query(ServiceRequest).filter(
        (ServiceRequest.receiver_id == user.id) | (ServiceRequest.requester_id == user.id)
    ).delete(synchronize_session=False)
    db.query(UserTransaction).filter(UserTransaction.user_id == user.id).delete(
        synchronize_session=False
    )
    db.query(WalletRecharge).filter(WalletRecharge.user_id == user.id).delete(
        synchronize_session=False
    )
    db.query(UserWallet).filter(UserWallet.user_id == user.id).delete(synchronize_session=False)
    db.query(ServiceOffer).filter(ServiceOffer.owner_id == user.id).delete(
        synchronize_session=False
    )
    db.delete(user)
    db.commit()
    return True

def update_user(
    db: Session,
    user_id: int,
    name: Optional[str] = None,
    surname: Optional[str] = None,
    avatar_key: Optional[str] = None,
) -> Optional[User]:
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    if name is not None:
        user.name = name
    if surname is not None:
        user.surname = surname
    if avatar_key is not None:
        user.avatar_key = avatar_key
    db.commit()
    db.refresh(user)
    return user

def update_password(db: Session, user_id: int, new_password: str) -> Optional[User]:
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    user.hashed_password = hash_password(new_password)
    db.commit()
    db.refresh(user)
    return user
