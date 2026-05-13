from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.auth import get_current_user
from app.schemas.review import CreateReviewPayload, CreateReviewResponse, TransactionReviewOut
from app.services.portal import PortalNotFoundError
from app.services.review import (
    create_review_response,
    get_service_reviews_response,
    get_transaction_reviews_response,
)

router = APIRouter()


@router.post("/reviews", response_model=CreateReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    payload: CreateReviewPayload,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        return create_review_response(
            db=db,
            reviewer_id=current_user.id,
            transaction_id=payload.transaction_id,
            rating=payload.rating,
            comment=payload.comment,
        )
    except PortalNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get(
    "/reviews/services/{service_offer_id}",
    response_model=list[TransactionReviewOut],
    status_code=status.HTTP_200_OK,
)
def get_service_reviews(
    service_offer_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        return get_service_reviews_response(db, service_offer_id)
    except PortalNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get(
    "/reviews/{transaction_id}",
    response_model=list[TransactionReviewOut],
    status_code=status.HTTP_200_OK,
)
def get_transaction_reviews(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        return get_transaction_reviews_response(db, current_user.id, transaction_id)
    except PortalNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

