from pydantic import BaseModel, Field


class TransactionReviewOut(BaseModel):
	id: int
	transaction_id: int
	service: str | None = None
	reviewer_id: int
	reviewer_name: str | None = None
	reviewed_user_id: int
	reviewed_user_name: str | None = None
	rating: int
	comment: str | None = None
	created_at: str

	class Config:
		from_attributes = True


class CreateReviewPayload(BaseModel):
	transaction_id: int
	rating: int = Field(..., ge=1, le=5)
	comment: str | None = Field(default=None, max_length=500)


class CreateReviewResponse(BaseModel):
	message: str
	review: TransactionReviewOut
