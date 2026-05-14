from sqlalchemy.orm import Session

from app.db.queries_chat import get_request_by_history_transaction_id
from app.db.queries_portal import (
	get_request_by_transaction_id,
	get_service_offer_by_id,
	get_transaction_by_id,
	mark_transaction_update_unseen,
)
from app.db.queries_review import (
	create_transaction_review,
	delete_transaction_review,
	get_review_by_transaction_id,
	list_reviews_by_reviewer_id,
	list_reviews_by_service_offer_id,
	list_reviews_by_transaction_id,
)
from app.models.portal import UserTransaction
from app.models.users import User
from app.schemas.portal import format_datetime
from app.schemas.review import CreateReviewResponse, TransactionReviewOut
from app.services.portal import PortalNotFoundError


def _display_name_for_user(user: User) -> str:
	full_name = " ".join(part for part in [user.name, user.surname] if part).strip()
	return full_name or user.email


def _user_name_map(db: Session, user_ids: set[int]) -> dict[int, str]:
	if not user_ids:
		return {}

	users = db.query(User).filter(User.id.in_(user_ids)).all()
	return {user.id: _display_name_for_user(user) for user in users}


def _reviewer_name_map(db: Session, reviews) -> dict[int, str]:
	return _user_name_map(db, {review.reviewer_id for review in reviews})


def _transaction_service_map(db: Session, reviews) -> dict[int, str]:
	transaction_ids = {review.transaction_id for review in reviews}
	if not transaction_ids:
		return {}

	transactions = db.query(UserTransaction).filter(UserTransaction.id.in_(transaction_ids)).all()
	return {transaction.id: transaction.service for transaction in transactions}


def _build_review_out(
	review,
	reviewer_name: str | None = None,
	reviewed_user_name: str | None = None,
	service: str | None = None,
) -> TransactionReviewOut:
	return TransactionReviewOut(
		id=review.id,
		transaction_id=review.transaction_id,
		service=service,
		reviewer_id=review.reviewer_id,
		reviewer_name=reviewer_name,
		reviewed_user_id=review.reviewed_user_id,
		reviewed_user_name=reviewed_user_name,
		rating=review.rating,
		comment=review.comment,
		created_at=format_datetime(review.created_at),
	)


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
	mark_transaction_update_unseen(db, request_row.seller_transaction_id)

	return CreateReviewResponse(
		message="Review created successfully",
		review=_build_review_out(
			review,
			_reviewer_name_map(db, [review]).get(review.reviewer_id),
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
	reviewer_names = _reviewer_name_map(db, reviews)

	return [
		_build_review_out(review, reviewer_names.get(review.reviewer_id))
		for review in reviews
	]


def get_service_reviews_response(
	db: Session,
	service_offer_id: int,
) -> list[TransactionReviewOut]:
	service_offer = get_service_offer_by_id(db, service_offer_id)
	if service_offer is None:
		raise PortalNotFoundError("Service not found")

	reviews = list_reviews_by_service_offer_id(db, service_offer_id)
	reviewer_names = _reviewer_name_map(db, reviews)

	return [
		_build_review_out(review, reviewer_names.get(review.reviewer_id))
		for review in reviews
	]


def get_user_reviews_for_admin_response(db: Session, reviewer_id: int) -> list[TransactionReviewOut]:
	reviews = list_reviews_by_reviewer_id(db, reviewer_id)
	user_names = _user_name_map(
		db,
		{user_id for review in reviews for user_id in [review.reviewer_id, review.reviewed_user_id]},
	)
	services = _transaction_service_map(db, reviews)

	return [
		_build_review_out(
			review,
			reviewer_name=user_names.get(review.reviewer_id),
			reviewed_user_name=user_names.get(review.reviewed_user_id),
			service=services.get(review.transaction_id),
		)
		for review in reviews
	]


def delete_review_for_admin_response(db: Session, review_id: int) -> None:
	if not delete_transaction_review(db, review_id):
		raise PortalNotFoundError("Review not found")
