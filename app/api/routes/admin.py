from fastapi import APIRouter, Depends, HTTPException, Response, status
from app.core.auth import check_admin
from app.schemas.user import UserOut

router = APIRouter()

@router.get("")
def admin_only(user: UserOut = Depends(check_admin)):
    return {"message": "Welcome, admin!"}