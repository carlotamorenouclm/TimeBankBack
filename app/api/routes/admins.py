from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import UserOut, UserUpdateRoleTimeTokens
from app.core.auth import check_admin
from app.db.queries_admin import (
    list_admins,
    update_role_time_tokens
)

router = APIRouter()


@router.get("", response_model=list[UserOut], status_code=status.HTTP_200_OK, 
            dependencies=[Depends(check_admin)])
def get_admins(db: Session = Depends(get_db)):
    return list_admins(db)


@router.post("/updateRoleTimeTokens/{user_id:int}", status_code=status.HTTP_200_OK,
             dependencies=[Depends(check_admin)])
def change_role_time_tokens(user_id: int, body: UserUpdateRoleTimeTokens, db: Session = Depends(get_db)):
    new_role = body.new_role.upper()
    new_time_tokens = body.new_time_tokens

    if new_role not in ["USER", "ADMIN"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    if new_time_tokens < 0:
        raise HTTPException(status_code=400, detail="Time tokens cannot be negative")
    
    user = update_role_time_tokens(db, user_id, new_role, new_time_tokens)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return Response(status_code=status.HTTP_200_OK, content="Role or/and time tokens updated successfully")