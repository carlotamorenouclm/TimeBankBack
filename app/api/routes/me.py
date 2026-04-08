from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import UserCreate, UserOut
from app.core.auth import check_admin, get_current_user
from app.db.queries_users import (
    add_user,
    list_users,
    delete_user,
    get_user_by_id,
    get_user_by_email,
)

router = APIRouter()

@router.get("", response_model=UserOut, status_code=status.HTTP_200_OK)
def me(current_user=Depends(get_current_user)):
    return current_user

@router.post("/isAdmin", response_model=bool, status_code=status.HTTP_200_OK)
def is_admin(current_user=Depends(get_current_user)):
    return current_user.role == "ADMIN"
