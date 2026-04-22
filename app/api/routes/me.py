# Routes related to the currently authenticated user.
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import UserOut, UserUpdate
from app.core.auth import get_current_user
from app.db.queries_users import (
    delete_user_account,
    update_user,
)

router = APIRouter()

@router.get("", response_model=UserOut, status_code=status.HTTP_200_OK)
def me(current_user=Depends(get_current_user)):
    return current_user


@router.post("/update", response_model=UserOut, status_code=status.HTTP_200_OK)
def update_me(
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user = update_user(db, current_user.id, payload.name, payload.surname, payload.avatar_key)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
def delete_me(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    ok = delete_user_account(db, current_user)
    if not ok:
        raise HTTPException(status_code=404, detail="User not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/isAdmin", response_model=bool, status_code=status.HTTP_200_OK)
def is_admin(current_user=Depends(get_current_user)):
    return current_user.role == "ADMIN"
