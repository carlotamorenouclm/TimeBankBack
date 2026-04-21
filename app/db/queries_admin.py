from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.users import User
from app.core.security import hash_password
from app.db.queries_users import get_user_by_id

def list_admins(db: Session) -> List[User]:
    return db.query(User).filter(User.role == "ADMIN").order_by(User.id.asc()).all()

def update_role_time_tokens(db: Session, user_id: int, new_role: str, new_time_tokens: int) -> Optional[User]:
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    user.role = new_role
    user.time_tokens = new_time_tokens
    db.commit()
    db.refresh(user)
    return user