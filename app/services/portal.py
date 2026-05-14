# Portal service layer: orchestrates queries and maps ORM models to DTOs.
import stripe
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.queries_chat import (
    count_unread_request_messages,
    count_unread_thread_messages,
    get_history_chat_info,
    get_request_by_history_transaction_id,
)
from app.db.queries_portal import (
    accept_request,
    complete_request,
    count_pending_received_requests,
    create_service_offer,
    create_purchase_request,
    create_wallet_recharge,
    delete_service_offer,
    get_service_offer_by_id,
    get_request_for_user,
    get_request_for_receiver,
    get_wallet_by_user_id,
    list_available_service_offers,
    list_owned_service_offers,
    list_received_requests,
    list_user_transactions,
    list_wallet_recharges,
    reject_request,
)
from app.db.queries_review import get_average_rating_by_service_offer_id
from app.schemas.portal import (
    CreateServiceOfferResponse,
    CreateServiceRequestResponse,
    DashboardResponse,
    DeleteServiceOfferResponse,
    HistoryResponse,
    InboxRequestOut,
    InboxResponse,
    PortalUserSummary,
    ServiceOfferOut,
    TransactionOut,
    WalletRechargeOut,
    WalletResponse,
    format_datetime,
)


class StripePaymentError(Exception):
    pass


def _configure_stripe() -> None:
    if not settings.STRIPE_SECRET_KEY:
        raise StripePaymentError("Stripe secret key is not configured")
    stripe.api_key = settings.STRIPE_SECRET_KEY


class PortalNotFoundError(Exception):
    # Domain-level exception so the service layer stays independent from FastAPI.
    pass


def build_portal_summary(db: Session, current_user) -> PortalUserSummary:
    # Convert the authenticated user into the DTO exposed by the API.
    full_name = " ".join(part for part in [current_user.name, current_user.surname] if part).strip()
    return PortalUserSummary(
        id=current_user.id,
        name=full_name or current_user.email,
        role=current_user.role,
        email=current_user.email,
        avatar_key=current_user.avatar_key,
        pending_inbox_count=count_pending_received_requests(db, current_user.id),
    )


def _build_service_offer_list(db: Session, offers) -> list[ServiceOfferOut]:
    # Reuse one ORM -> DTO conversion path for every service list response.
    return [_build_service_offer_response(db, item) for item in offers]


def _build_service_offer_response(db: Session, offer) -> ServiceOfferOut:
    # Keep single-item service mapping aligned with list responses.
    return ServiceOfferOut.model_validate(offer).model_copy(
        update={
            "overall_rating": get_average_rating_by_service_offer_id(db, offer.id),
        }
    )


def get_dashboard_response(db: Session, user_id: int) -> DashboardResponse:
    # Split purchasable services from owned services to support catalog tabs.
    services = _build_service_offer_list(db, list_available_service_offers(db, user_id))
    my_services = _build_service_offer_list(db, list_owned_service_offers(db, user_id))
    return DashboardResponse(services=services, my_services=my_services)


def get_history_response(db: Session, user_id: int) -> HistoryResponse:
    # Build the history response by mapping each database row into TransactionOut.
    transactions = []
    for item in list_user_transactions(db, user_id):
        linked_request = get_request_by_history_transaction_id(db, item.id)
        chat_key, other_user_id = get_history_chat_info(db, item)
        unread_count = (
            count_unread_request_messages(db, linked_request.id, user_id)
            if linked_request is not None
            else count_unread_thread_messages(db, chat_key, user_id)
            if chat_key
            else 0
        )
        transactions.append(
            TransactionOut(
            id=item.id,
            request_id=linked_request.id if linked_request is not None else None,
            chat_key=chat_key,
            other_user_id=other_user_id,
            unread_count=unread_count,
            type=item.type,
            service=item.service,
            other_user=item.other_user,
            date=linked_request.scheduled_at if linked_request is not None else format_datetime(item.occurred_at),
            address=linked_request.address if linked_request is not None else None,
            amount=item.amount,
            status=item.status,
            clarification=(
                linked_request.clarification if linked_request is not None else None
            ),
            reject_reason=(
                linked_request.reject_reason if linked_request is not None else None
            ),
            )
        )

    existing_transaction_ids = {item.id for item in list_user_transactions(db, user_id)}
    for request_row in list_received_requests(db, user_id):
        if (
            request_row.status != "rejected"
            or request_row.seller_transaction_id in existing_transaction_ids
        ):
            continue

        transactions.append(
            TransactionOut(
                id=-request_row.id,
                request_id=request_row.id,
                chat_key=None,
                other_user_id=request_row.requester_id,
                unread_count=count_unread_request_messages(db, request_row.id, user_id),
                type="Sale",
                service=request_row.service,
                other_user=request_row.requester_name,
                date=request_row.scheduled_at,
                address=request_row.address,
                amount=0,
                status="Rejected",
                clarification=None,
                reject_reason=request_row.reject_reason,
            )
        )
    return HistoryResponse(transactions=transactions)


def _build_inbox_response(request_rows) -> InboxResponse:
    # Keep inbox mapping in one place so GET and accept/reject share the same format.
    requests = [
        InboxRequestOut(
            id=item.id,
            service=item.service,
            description=item.description,
            date=item.scheduled_at,
            address=item.address,
            message=item.message,
            image_key=item.image_key,
            price=item.price,
            status=item.status,
            clarification=item.clarification,
            reject_reason=item.reject_reason,
            requester_name=item.requester_name,
        )
        for item in request_rows
    ]
    return InboxResponse(requests=requests)


def get_inbox_response(db: Session, user_id: int) -> InboxResponse:
    return _build_inbox_response(list_received_requests(db, user_id))


def accept_inbox_request_response(
    db: Session,
    user_id: int,
    request_id: int,
    clarification: str,
) -> InboxResponse:
    request_row = get_request_for_receiver(db, request_id, user_id)
    if request_row is None:
        raise PortalNotFoundError("Request not found")

    # Return the refreshed inbox after updating the request state.
    accept_request(db, request_row, clarification)
    return get_inbox_response(db, user_id)


def reject_inbox_request_response(
    db: Session,
    user_id: int,
    request_id: int,
    reason: str,
) -> InboxResponse:
    request_row = get_request_for_receiver(db, request_id, user_id)
    if request_row is None:
        raise PortalNotFoundError("Request not found")

    reject_request(db, request_row, reason)
    return get_inbox_response(db, user_id)


def complete_request_response(db: Session, user_id: int, request_id: int) -> HistoryResponse:
    request_row = get_request_for_user(db, request_id, user_id)
    if request_row is None:
        raise PortalNotFoundError("Request not found")

    try:
        complete_request(db, request_row)
    except ValueError as exc:
        raise PortalNotFoundError(str(exc)) from exc

    return get_history_response(db, user_id)


def get_wallet_response(db: Session, user_id: int) -> WalletResponse:
    wallet = get_wallet_by_user_id(db, user_id)
    if wallet is None:
        raise PortalNotFoundError("Wallet not found")

    # Wallet data and its recharges are returned in one DTO ready for HTTP.
    recharges = [
        WalletRechargeOut(id=item.id, date=format_datetime(item.created_at), amount=item.amount)
        for item in list_wallet_recharges(db, user_id)
    ]
    return WalletResponse(balance=wallet.balance, status=wallet.status, recharges=recharges)


def recharge_wallet_response(db: Session, user_id: int, amount: int) -> WalletResponse:
    try:
        create_wallet_recharge(db, user_id, amount)
    except ValueError as exc:
        raise PortalNotFoundError(str(exc)) from exc

    # Reuse the same response builder so every wallet response keeps one format.
    return get_wallet_response(db, user_id)


def create_wallet_checkout_session_response(user_id: int, amount: int) -> dict:
    _configure_stripe()

    unit_amount = settings.STRIPE_COIN_UNIT_AMOUNT_CENTS
    if unit_amount <= 0:
        raise StripePaymentError("Stripe coin price is not configured")

    base_url = settings.FRONTEND_URL.rstrip("/")
    try:
        session = stripe.checkout.Session.create(
            mode="payment",
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": settings.STRIPE_CURRENCY,
                        "product_data": {"name": f"TimeBank wallet recharge ({amount} coins)"},
                        "unit_amount": unit_amount,
                    },
                    "quantity": amount,
                }
            ],
            metadata={"user_id": str(user_id), "amount": str(amount)},
            payment_intent_data={"metadata": {"user_id": str(user_id), "amount": str(amount)}},
            success_url=f"{base_url}/wallet?stripe_session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{base_url}/wallet?stripe_cancelled=1",
        )
    except stripe.error.StripeError as exc:
        raise StripePaymentError(str(exc)) from exc

    return {"session_id": session.id, "checkout_url": session.url}


def confirm_wallet_checkout_session_response(db: Session, user_id: int, session_id: str) -> WalletResponse:
    _configure_stripe()

    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except stripe.error.StripeError as exc:
        raise StripePaymentError(str(exc)) from exc

    if str(session.metadata.get("user_id")) != str(user_id):
        raise PortalNotFoundError("Checkout session does not belong to this user")

    if session.payment_status != "paid":
        raise StripePaymentError("Payment has not been completed")

    try:
        amount = int(session.metadata.get("amount", "0"))
        if amount <= 0:
            raise ValueError("Invalid recharge amount")
        create_wallet_recharge(db, user_id, amount, session.id)
    except ValueError as exc:
        raise PortalNotFoundError(str(exc)) from exc

    return get_wallet_response(db, user_id)


def process_stripe_checkout_completed(db: Session, checkout_session: dict) -> None:
    metadata = checkout_session.get("metadata") or {}
    if checkout_session.get("payment_status") != "paid":
        return

    try:
        user_id = int(metadata.get("user_id", "0"))
        amount = int(metadata.get("amount", "0"))
    except ValueError:
        raise StripePaymentError("Invalid Stripe checkout metadata")

    if user_id <= 0 or amount <= 0:
        raise StripePaymentError("Invalid Stripe checkout metadata")

    try:
        create_wallet_recharge(db, user_id, amount, checkout_session["id"])
    except ValueError as exc:
        raise PortalNotFoundError(str(exc)) from exc


def create_purchase_request_response(
    db: Session,
    requester,
    service_offer_id: int,
    scheduled_at: str,
    street: str,
    street_number: str,
    floor: str | None,
    door: str | None,
    message: str | None,
) -> CreateServiceRequestResponse:
    # Orchestrate request creation and return the requester balance to the frontend.
    service_offer = get_service_offer_by_id(db, service_offer_id)
    if service_offer is None:
        raise PortalNotFoundError("Service not found")
    if not service_offer.is_visible:
        raise PortalNotFoundError("Service is not available")

    address_parts = [f"{street} No. {street_number}"]
    if floor:
        address_parts.append(f"Floor {floor}")
    if door:
        address_parts.append(f"Door {door}")
    address = ", ".join(address_parts)

    try:
        purchase_request = create_purchase_request(
            db=db,
            requester=requester,
            service_offer=service_offer,
            scheduled_at=scheduled_at,
            address=address,
            message=message,
        )
    except ValueError as exc:
        raise PortalNotFoundError(str(exc)) from exc

    wallet = get_wallet_by_user_id(db, requester.id)
    new_balance = wallet.balance if wallet is not None else 0

    return CreateServiceRequestResponse(
        request_id=purchase_request.id,
        message="Purchase request created successfully",
        new_balance=new_balance,
    )


def create_service_offer_response(
    db: Session,
    provider,
    title: str,
    description: str,
    availability: str,
    home_service: bool,
    street: str | None,
    street_number: str | None,
    floor: str | None,
    door: str | None,
    extra: str | None,
    price: int,
    image_key: str,
) -> CreateServiceOfferResponse:
    # Create a new published service and return it ready for the frontend.
    address = None
    if not home_service and street and street_number:
        address_parts = [f"{street.strip()} No. {street_number.strip()}"]
        if floor:
            address_parts.append(f"Floor {floor.strip()}")
        if door:
            address_parts.append(f"Door {door.strip()}")
        address = ", ".join(address_parts)

    service_offer = create_service_offer(
        db=db,
        provider=provider,
        title=title.strip(),
        description=description.strip(),
        availability=availability.strip(),
        home_service=home_service,
        address=address,
        extra=extra.strip() if extra else None,
        price=price,
        image_key=image_key.strip(),
    )
    return CreateServiceOfferResponse(
        message="Service published successfully",
        service=_build_service_offer_response(db, service_offer),
    )


def delete_service_offer_response(
    db: Session,
    provider_id: int,
    service_offer_id: int,
) -> DeleteServiceOfferResponse:
    # Delete one owned service and return a lightweight confirmation payload.
    service_offer = get_service_offer_by_id(db, service_offer_id)
    if service_offer is None:
        raise PortalNotFoundError("Service not found")

    if service_offer.owner_id != provider_id:
        raise PortalNotFoundError("You can only delete your own services")

    try:
        deleted_service_id = delete_service_offer(db, service_offer)
    except ValueError as exc:
        raise PortalNotFoundError(str(exc)) from exc

    return DeleteServiceOfferResponse(
        message="Service deleted successfully",
        deleted_service_id=deleted_service_id,
    )
