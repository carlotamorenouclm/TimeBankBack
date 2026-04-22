# Admin-area routes for listing admins and updating user roles.
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import UserOut, UserUpdateRole
from app.core.auth import check_admin
from app.db.queries_admin import (
    list_admins,
    update_user_role
)

router = APIRouter()


@router.get("", response_model=list[UserOut], status_code=status.HTTP_200_OK, 
            dependencies=[Depends(check_admin)])
def get_admins(db: Session = Depends(get_db)):
    return list_admins(db)


@router.post("/updateRole/{user_id:int}", status_code=status.HTTP_200_OK,
             dependencies=[Depends(check_admin)])
def change_role(user_id: int, body: UserUpdateRole, db: Session = Depends(get_db)):
    new_role = body.new_role.upper()

    if new_role not in ["USER", "ADMIN"]:
        raise HTTPException(status_code=400, detail="Invalid role")

    user = update_user_role(db, user_id, new_role)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return Response(status_code=status.HTTP_200_OK, content="Role updated successfully")
