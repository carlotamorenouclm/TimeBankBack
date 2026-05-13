# Admin-area routes for listing admins and updating user roles.
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import UserOut, UserUpdateRole, UserUpdateActive
from app.schemas.portal import HistoryResponse, WalletResponse
from app.schemas.review import TransactionReviewOut
from app.core.auth import check_admin
from app.db.queries_admin import (
    list_admins,
    update_user_role,
    update_user_is_active
)
from app.db.queries_users import get_user_by_id
from app.services.portal import get_history_response, get_wallet_response, PortalNotFoundError
from app.services.review import (
    delete_review_for_admin_response,
    get_user_reviews_for_admin_response,
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


@router.post("/update/is-active/{user_id:int}", status_code=status.HTTP_200_OK,
             dependencies=[Depends(check_admin)])
def change_is_active(user_id: int, body: UserUpdateActive, db: Session = Depends(get_db)):
    user = update_user_is_active(db, user_id, body.is_active)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return Response(
        status_code=status.HTTP_200_OK,
        content="User active status updated successfully"
    )


@router.get("/wallet/history", response_model=WalletResponse, status_code=status.HTTP_200_OK,
            dependencies=[Depends(check_admin)])
def get_user_wallet_history(user_id: int, db: Session = Depends(get_db)):
    if get_user_by_id(db, user_id) is None:
        raise HTTPException(status_code=404, detail="User not found")
    try:
        return get_wallet_response(db, user_id)
    except PortalNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/transaction/history", response_model=HistoryResponse, status_code=status.HTTP_200_OK,
            dependencies=[Depends(check_admin)])
def get_user_transaction_history(user_id: int, db: Session = Depends(get_db)):
    if get_user_by_id(db, user_id) is None:
        raise HTTPException(status_code=404, detail="User not found")
    return get_history_response(db, user_id)


@router.get("/reviews", response_model=list[TransactionReviewOut], status_code=status.HTTP_200_OK,
            dependencies=[Depends(check_admin)])
def get_user_reviews(user_id: int, db: Session = Depends(get_db)):
    if get_user_by_id(db, user_id) is None:
        raise HTTPException(status_code=404, detail="User not found")
    return get_user_reviews_for_admin_response(db, user_id)


@router.delete("/reviews/{review_id:int}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(check_admin)])
def delete_user_review(review_id: int, db: Session = Depends(get_db)):
    try:
        delete_review_for_admin_response(db, review_id)
    except PortalNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
