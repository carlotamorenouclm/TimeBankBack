from typing import Optional, List
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.models.users import User

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def add_user(db: Session, email: str, password: str, name: Optional[str] = None, surname: Optional[str] = None) -> User:
    hashed = pwd_context.hash(password)
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
    return db.query(User).order_by(User.id.asc()).all()


def delete_user(db: Session, user_id: int) -> bool:
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True

from app.core.security import verify_password


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def update_user_profile(
    db: Session,
    user: User,
    name: Optional[str] = None,
    surname: Optional[str] = None,
    email: Optional[str] = None,
) -> User:
    if name is not None:
        user.name = name
    if surname is not None:
        user.surname = surname
    if email is not None:
        user.email = email

    db.commit()
    db.refresh(user)
    return user