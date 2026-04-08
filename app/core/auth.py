from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.security import decode_token, verify_password
from app.db.queries_users import get_user_by_email
from app.schemas.user import UserOut
from app.db.session import get_db


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def aut_user( email: str, password: str, db: Session = Depends(get_db)) -> UserOut:
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user

async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> UserOut:
    payload = decode_token(token)
    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = get_user_by_email(db, email)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    if user.is_active is False:
        raise HTTPException(status_code=403, detail="Inactive user")
    return user

def check_admin(user: UserOut = Depends(get_current_user)):
    if user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return user