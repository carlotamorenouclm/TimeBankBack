from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.users import User
from app.core.security import hash_password


def add_user(db: Session, email: str, password: str, name: Optional[str] = None, surname: Optional[str] = None) -> User:
    hashed = hash_password(password)
    user = User(email=email, hashed_password=hashed, name=name, surname=surname)
    db.add(user)
    db.commit()
    db.refresh(user)
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
    db.delete(user)
    db.commit()
    return True

def update_user(db: Session, user_id: int, email: Optional[str] = None, password: Optional[str] = None, name: Optional[str] = None, surname: Optional[str] = None) -> Optional[User]:
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    if name is not None:
        user.name = name
    if surname is not None:
        user.surname = surname
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

