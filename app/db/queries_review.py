"""Queries for transaction reviews."""
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.portal import ServiceRequest
from app.models.review import TransactionReview


def get_review_by_transaction_id(db: Session, transaction_id: int) -> TransactionReview | None:
	return (
		db.query(TransactionReview)
		.filter(TransactionReview.transaction_id == transaction_id)
		.first()
	)


def list_reviews_by_transaction_id(db: Session, transaction_id: int) -> list[TransactionReview]:
	return (
		db.query(TransactionReview)
		.filter(TransactionReview.transaction_id == transaction_id)
		.order_by(TransactionReview.id.asc())
		.all()
	)


def list_reviews_by_reviewer_id(db: Session, reviewer_id: int) -> list[TransactionReview]:
	return (
		db.query(TransactionReview)
		.filter(TransactionReview.reviewer_id == reviewer_id)
		.order_by(TransactionReview.created_at.desc(), TransactionReview.id.desc())
		.all()
	)


def list_reviews_by_service_offer_id(db: Session, service_offer_id: int) -> list[TransactionReview]:
	return (
		db.query(TransactionReview)
		.join(ServiceRequest, ServiceRequest.buyer_transaction_id == TransactionReview.transaction_id)
		.filter(ServiceRequest.service_offer_id == service_offer_id)
		.order_by(TransactionReview.id.asc())
		.all()
	)


def get_average_rating_by_service_offer_id(db: Session, service_offer_id: int) -> float | None:
	average_rating = (
		db.query(func.avg(TransactionReview.rating))
		.join(ServiceRequest, ServiceRequest.buyer_transaction_id == TransactionReview.transaction_id)
		.filter(ServiceRequest.service_offer_id == service_offer_id)
		.scalar()
	)
	return round(float(average_rating), 1) if average_rating is not None else None


def delete_transaction_review(db: Session, review_id: int) -> bool:
	review = db.query(TransactionReview).filter(TransactionReview.id == review_id).first()
	if review is None:
		return False

	db.delete(review)
	db.commit()
	return True


def create_transaction_review(
	db: Session,
	transaction_id: int,
	reviewer_id: int,
	reviewed_user_id: int,
	rating: int,
	comment: str | None,
) -> TransactionReview:
	review = TransactionReview(
		transaction_id=transaction_id,
		reviewer_id=reviewer_id,
		reviewed_user_id=reviewed_user_id,
		rating=rating,
		comment=comment.strip() if comment else None,
	)
	db.add(review)
	db.commit()
	db.refresh(review)
	return review
