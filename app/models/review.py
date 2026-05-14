"""
Define modelos SQLAlchemy que representan tablas de la base de datos.

Comentarios generados para documentar la intencion de cada bloque principal.
"""
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from app.models.users import Base

# Define esta clase y agrupa los datos que pertenecen a la entidad.
class TransactionReview(Base):
    __tablename__ = "transaction_reviews"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("user_transactions.id"), nullable=False, unique=True)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    reviewed_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    rating = Column(Integer, nullable=False)
    comment = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
