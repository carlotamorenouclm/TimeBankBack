from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import UserCreate, UserOut
from app.core.auth import check_admin
from app.db.queries_users import (
    add_user,
    list_users,
    delete_user,
    get_user_by_id,
    get_user_by_email,
)

router = APIRouter()


@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_email(db, payload.email):
        raise HTTPException(status_code=409, detail="Error registering")
    return add_user(db, payload.email, payload.password, payload.name, payload.surname)

@router.get("", response_model=list[UserOut], status_code=status.HTTP_200_OK, 
            dependencies=[Depends(check_admin)])
def get_users(db: Session = Depends(get_db)):
    return list_users(db)


@router.get("/{user_id:int}", response_model=UserOut, status_code=status.HTTP_200_OK, 
            dependencies=[Depends(check_admin)])
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/delete/{user_id}", status_code=status.HTTP_204_NO_CONTENT, 
               dependencies=[Depends(check_admin)])
def remove_user(user_id: int, db: Session = Depends(get_db)):
    ok = delete_user(db, user_id)
    if not ok:
        raise HTTPException(status_code=404, detail="User not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
