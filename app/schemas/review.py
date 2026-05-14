"""
Define esquemas Pydantic para validar entradas y serializar respuestas.

Comentarios generados para documentar la intencion de cada bloque principal.
"""
from pydantic import BaseModel, Field


# Define esta clase y agrupa los datos que pertenecen a la entidad.
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

	# Define esta clase y agrupa los datos que pertenecen a la entidad.
	class Config:
		from_attributes = True


# Define esta clase y agrupa los datos que pertenecen a la entidad.
class CreateReviewPayload(BaseModel):
	transaction_id: int
	rating: int = Field(..., ge=1, le=5)
	comment: str | None = Field(default=None, max_length=500)


# Define esta clase y agrupa los datos que pertenecen a la entidad.
class CreateReviewResponse(BaseModel):
	message: str
	review: TransactionReviewOut
