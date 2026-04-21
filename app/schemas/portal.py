from datetime import datetime

from pydantic import BaseModel, Field


class PortalUserSummary(BaseModel):
    id: int
    name: str
    role: str
    email: str


class ServiceOfferOut(BaseModel):
    id: int
    title: str
    description: str
    availability: str
    extra: str | None = None
    price: int
    image_key: str
    owner_name: str

    class Config:
        from_attributes = True


class DashboardResponse(BaseModel):
    services: list[ServiceOfferOut]


class TransactionOut(BaseModel):
    id: int
    type: str
    service: str
    other_user: str | None = None
    date: str
    amount: int
    status: str


class HistoryResponse(BaseModel):
    transactions: list[TransactionOut]


class InboxRequestOut(BaseModel):
    id: int
    service: str
    description: str
    date: str
    address: str
    message: str | None = None
    image_key: str
    price: int
    status: str
    clarification: str | None = None
    reject_reason: str | None = None
    requester_name: str


class InboxResponse(BaseModel):
    requests: list[InboxRequestOut]


class AcceptRequestPayload(BaseModel):
    clarification: str = Field(default="", max_length=500)


class RejectRequestPayload(BaseModel):
    reason: str = Field(..., min_length=1, max_length=500)


class WalletRechargeOut(BaseModel):
    id: int
    date: str
    amount: int


class WalletResponse(BaseModel):
    balance: int
    status: str
    recharges: list[WalletRechargeOut]


class RechargePayload(BaseModel):
    amount: int = Field(..., gt=0, le=1000)


def format_datetime(value: datetime) -> str:
    return value.strftime("%Y-%m-%d")
