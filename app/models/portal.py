from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from app.models.users import Base


class ServiceOffer(Base):
    __tablename__ = "service_offers"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    availability = Column(String(255), nullable=False)
    extra = Column(String(255), nullable=True)
    price = Column(Integer, nullable=False)
    image_key = Column(String(50), nullable=False)
    owner_name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class ServiceRequest(Base):
    __tablename__ = "service_requests"

    id = Column(Integer, primary_key=True, index=True)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    requester_name = Column(String(255), nullable=False)
    service = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    scheduled_at = Column(String(255), nullable=False)
    address = Column(String(255), nullable=False)
    message = Column(Text, nullable=True)
    image_key = Column(String(50), nullable=False)
    price = Column(Integer, nullable=False)
    status = Column(String(20), default="pending", nullable=False)
    clarification = Column(Text, nullable=True)
    reject_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class UserWallet(Base):
    __tablename__ = "user_wallets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    balance = Column(Integer, default=42, nullable=False)
    status = Column(String(20), default="Active", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class WalletRecharge(Base):
    __tablename__ = "wallet_recharges"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_wallets.user_id"), nullable=False, index=True)
    amount = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class UserTransaction(Base):
    __tablename__ = "user_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    type = Column(String(20), nullable=False)
    service = Column(String(255), nullable=False)
    other_user = Column(String(255), nullable=True)
    amount = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False)
    occurred_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
