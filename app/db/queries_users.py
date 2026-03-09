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