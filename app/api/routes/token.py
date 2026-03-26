from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.auth import aut_user
from app.core.security import create_access_token
from app.db.session import get_db
from app.schemas.token import Token

from app.schemas.user import UserOut

router = APIRouter()

@router.post("/token", response_model=Token, tags=["auth"])
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = aut_user(db=db, email=form_data.username, password=form_data.password)
    if user.is_active is False:
        raise HTTPException(status_code=403, detail="Inactive user")
    access_token = create_access_token(data={"sub": user.email})
    return Token(access_token=access_token)

