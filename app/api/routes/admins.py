from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import UserOut
from app.core.auth import check_admin
from app.db.queries_admin import (
    list_admins,
    update_role,
    update_time_tokens,
)

router = APIRouter()

@router.get("", response_model=list[UserOut], status_code=status.HTTP_200_OK, 
            dependencies=[Depends(check_admin)])
def get_admins(db: Session = Depends(get_db)):
    return list_admins(db)

@router.post("/updateRole/{user_id:int}", status_code=status.HTTP_200_OK,
             dependencies=[Depends(check_admin)])
def change_role(user_id: int, new_role: str, db: Session = Depends(get_db)):
    new_role = new_role.upper()
    if new_role not in ["USER", "ADMIN"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    user = update_role(db, user_id, new_role)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return Response(status_code=status.HTTP_200_OK, content="Role updated successfully")

@router.post("/updateTimeTokens/{user_id:int}", status_code=status.HTTP_200_OK,
             dependencies=[Depends(check_admin)])
def change_time_tokens(user_id: int, new_time_tokens: int, db: Session = Depends(get_db)):
    if new_time_tokens < 0:
        raise HTTPException(status_code=400, detail="Time tokens cannot be negative")
    user = update_time_tokens(db, user_id, new_time_tokens)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return Response(status_code=status.HTTP_200_OK, content="Time tokens updated successfully")