"""
Define esquemas Pydantic para validar entradas y serializar respuestas.

Comentarios generados para documentar la intencion de cada bloque principal.
"""
# Pydantic DTOs and payloads for the portal area that travel through the API.
from datetime import datetime

from pydantic import BaseModel, Field, model_validator


# Define esta clase y agrupa los datos que pertenecen a la entidad.
class PortalUserSummary(BaseModel):
    id: int
    name: str
    role: str
    email: str
    avatar_key: str | None = None
    pending_inbox_count: int = 0
    pending_purchases_count: int = 0
    pending_sales_count: int = 0


# Define esta clase y agrupa los datos que pertenecen a la entidad.
class ServiceOfferOut(BaseModel):
    id: int
    owner_id: int | None = None
    title: str
    description: str
    availability: str
    home_service: bool
    address: str | None = None
    extra: str | None = None
    price: int
    image_key: str
    owner_name: str
    is_visible: bool = True
    overall_rating: float | None = None

    # Define esta clase y agrupa los datos que pertenecen a la entidad.
    class Config:
        from_attributes = True


# Define esta clase y agrupa los datos que pertenecen a la entidad.
class DashboardResponse(BaseModel):
    services: list[ServiceOfferOut]
    my_services: list[ServiceOfferOut] = []


# Define esta clase y agrupa los datos que pertenecen a la entidad.
class TransactionOut(BaseModel):
    id: int
    request_id: int | None = None
    chat_key: str | None = None
    other_user_id: int | None = None
    unread_count: int = 0
    has_unseen_update: bool = False
    has_unseen_review: bool = False
    type: str
    service: str
    other_user: str | None = None
    date: str
    address: str | None = None
    amount: int
    status: str
    clarification: str | None = None
    reject_reason: str | None = None


# Define esta clase y agrupa los datos que pertenecen a la entidad.
class HistoryResponse(BaseModel):
    transactions: list[TransactionOut]


# Define esta clase y agrupa los datos que pertenecen a la entidad.
class MarkHistoryNotificationsPayload(BaseModel):
    transaction_type: str = Field(..., pattern="^(Purchase|Sale)$")


# Define esta clase y agrupa los datos que pertenecen a la entidad.
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


# Define esta clase y agrupa los datos que pertenecen a la entidad.
class InboxResponse(BaseModel):
    requests: list[InboxRequestOut]


# Define esta clase y agrupa los datos que pertenecen a la entidad.
class AcceptRequestPayload(BaseModel):
    clarification: str = Field(default="", max_length=500)


# Define esta clase y agrupa los datos que pertenecen a la entidad.
class RejectRequestPayload(BaseModel):
    reason: str = Field(..., min_length=1, max_length=500)


# Define esta clase y agrupa los datos que pertenecen a la entidad.
class WalletRechargeOut(BaseModel):
    id: int
    date: str
    amount: int


# Define esta clase y agrupa los datos que pertenecen a la entidad.
class WalletResponse(BaseModel):
    balance: int
    status: str
    recharges: list[WalletRechargeOut]


# Define esta clase y agrupa los datos que pertenecen a la entidad.
class RechargePayload(BaseModel):
    amount: int = Field(..., gt=0, le=1000)


# Define esta clase y agrupa los datos que pertenecen a la entidad.
class StripeCheckoutSessionResponse(BaseModel):
    session_id: str
    checkout_url: str


# Define esta clase y agrupa los datos que pertenecen a la entidad.
class CreateServiceRequestPayload(BaseModel):
    scheduled_at: str = Field(..., min_length=3, max_length=255)
    street: str = Field(..., min_length=2, max_length=255)
    street_number: str = Field(..., min_length=1, max_length=30)
    floor: str | None = Field(default=None, max_length=30)
    door: str | None = Field(default=None, max_length=30)
    message: str | None = Field(default=None, max_length=500)


# Define esta clase y agrupa los datos que pertenecen a la entidad.
class CreateServiceRequestResponse(BaseModel):
    request_id: int
    message: str
    new_balance: int


# Define esta clase y agrupa los datos que pertenecen a la entidad.
class CreateServiceOfferPayload(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=10, max_length=1000)
    availability: str = Field(..., min_length=3, max_length=255)
    home_service: bool = True
    street: str | None = Field(default=None, min_length=2, max_length=255)
    street_number: str | None = Field(default=None, min_length=1, max_length=30)
    floor: str | None = Field(default=None, max_length=30)
    door: str | None = Field(default=None, max_length=30)
    extra: str | None = Field(default=None, max_length=255)
    price: int = Field(..., gt=0, le=1000)
    image_key: str = Field(..., min_length=2, max_length=12_000_000)

    # Encapsula una parte concreta de la logica de la aplicacion.
    @model_validator(mode="after")
    def validate_location(self):
        if not self.home_service and (not self.street or not self.street_number):
            raise ValueError("Street and street number are required when the service is not home service")

        if self.home_service:
            self.street = None
            self.street_number = None
            self.floor = None
            self.door = None

        return self


# Define esta clase y agrupa los datos que pertenecen a la entidad.
class CreateServiceOfferResponse(BaseModel):
    message: str
    service: ServiceOfferOut


# Define esta clase y agrupa los datos que pertenecen a la entidad.
class DeleteServiceOfferResponse(BaseModel):
    message: str
    deleted_service_id: int


# Define esta clase y agrupa los datos que pertenecen a la entidad.
class UpdateServiceVisibilityPayload(BaseModel):
    is_visible: bool


# Encapsula una parte concreta de la logica de la aplicacion.
def format_datetime(value: datetime) -> str:
    # Single date format for values returned to the frontend.
    return value.strftime("%Y-%m-%d")
