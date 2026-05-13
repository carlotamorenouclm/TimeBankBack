# Database queries used by the admin panel.
from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.portal import UserWallet
from app.models.users import User
from app.db.queries_users import get_user_by_id

def list_admins(db: Session) -> List[User]:
    return db.query(User).filter(User.role == "ADMIN").order_by(User.id.asc()).all()

def update_user_role(db: Session, user_id: int, new_role: str) -> Optional[User]:
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    user.role = new_role
    db.commit()
    db.refresh(user)
    return user


def update_user_is_active(db: Session, user_id: int, is_active: bool) -> Optional[User]:
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    user.is_active = is_active
    db.commit()
    db.refresh(user)
    return user


def update_user_wallet_balance(db: Session, user_id: int, coins: int) -> Optional[UserWallet]:
    user = get_user_by_id(db, user_id)
    if not user:
        return None

    wallet = db.query(UserWallet).filter(UserWallet.user_id == user_id).first()
    if wallet is None:
        wallet = UserWallet(user_id=user_id, balance=coins, status="Active")
        db.add(wallet)
    else:
        wallet.balance = coins

    db.commit()
    db.refresh(wallet)
    return wallet
