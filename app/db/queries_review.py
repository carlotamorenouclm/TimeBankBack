"""Queries for transaction reviews."""
from sqlalchemy.orm import Session

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
