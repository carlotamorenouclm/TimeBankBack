from sqlalchemy.orm import Session

from app.db.queries_chat import get_request_by_history_transaction_id
from app.db.queries_portal import get_request_by_transaction_id, get_transaction_by_id
from app.db.queries_review import (
	create_transaction_review,
	get_review_by_transaction_id,
	list_reviews_by_transaction_id,
)
from app.schemas.portal import format_datetime
from app.schemas.review import CreateReviewResponse, TransactionReviewOut
from app.services.portal import PortalNotFoundError


def create_review_response(
	db: Session,
	reviewer_id: int,
	transaction_id: int,
	rating: int,
	comment: str | None,
) -> CreateReviewResponse:
	transaction = get_transaction_by_id(db, transaction_id)
	if transaction is None:
		raise PortalNotFoundError("Transaction not found")

	if transaction.user_id != reviewer_id:
		raise PortalNotFoundError("You can only review your own transactions")

	if transaction.status != "Completed":
		raise PortalNotFoundError("Only completed transactions can be reviewed")

	if transaction.type != "Purchase":
		raise PortalNotFoundError("Only purchase transactions can be reviewed")

	request_row = get_request_by_transaction_id(db, transaction_id)
	if request_row is None or request_row.requester_id != reviewer_id:
		raise PortalNotFoundError("Review request not found")

	existing_review = get_review_by_transaction_id(db, transaction_id)
	if existing_review is not None:
		raise PortalNotFoundError("This transaction already has a review")

	review = create_transaction_review(
		db=db,
		transaction_id=transaction_id,
		reviewer_id=reviewer_id,
		reviewed_user_id=request_row.receiver_id,
		rating=rating,
		comment=comment,
	)

	return CreateReviewResponse(
		message="Review created successfully",
		review=TransactionReviewOut(
			id=review.id,
			transaction_id=review.transaction_id,
			reviewer_id=review.reviewer_id,
			reviewed_user_id=review.reviewed_user_id,
			rating=review.rating,
			comment=review.comment,
			created_at=format_datetime(review.created_at),
		),
	)


def get_transaction_reviews_response(
	db: Session,
	user_id: int,
	transaction_id: int,
) -> list[TransactionReviewOut]:
	transaction = get_transaction_by_id(db, transaction_id)
	if transaction is None:
		raise PortalNotFoundError("Transaction not found")

	request_row = get_request_by_history_transaction_id(db, transaction_id)
	if request_row is None:
		raise PortalNotFoundError("Review request not found")

	if user_id not in {request_row.requester_id, request_row.receiver_id}:
		raise PortalNotFoundError("You can only view reviews for your transactions")

	review_transaction_id = request_row.buyer_transaction_id or transaction_id
	reviews = list_reviews_by_transaction_id(db, review_transaction_id)

	return [
		TransactionReviewOut(
			id=review.id,
			transaction_id=review.transaction_id,
			reviewer_id=review.reviewer_id,
			reviewed_user_id=review.reviewed_user_id,
			rating=review.rating,
			comment=review.comment,
			created_at=format_datetime(review.created_at),
		)
		for review in reviews
	]
