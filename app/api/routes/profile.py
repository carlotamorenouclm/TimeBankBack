from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import UserOut, UserUpdate
from app.db.queries_users import get_user_by_email, update_user_profile
from app.api.routes.auth import get_current_user

router = APIRouter()


@router.put("", response_model=UserOut)
def update_profile(
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if payload.email and payload.email != current_user.email:
        existing_user = get_user_by_email(db, payload.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ese email ya está en uso"
            )

    updated_user = update_user_profile(
        db=db,
        user=current_user,
        name=payload.name,
        surname=payload.surname,
        email=payload.email,
    )

    return updated_user