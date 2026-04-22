# Portal service layer: orchestrates queries and maps ORM models to DTOs.
from sqlalchemy.orm import Session

from app.db.queries_portal import (
    accept_request,
    create_service_offer,
    create_purchase_request,
    create_wallet_recharge,
    delete_service_offer,
    get_request_by_transaction_id,
    get_service_offer_by_id,
    get_request_for_receiver,
    get_wallet_by_user_id,
    list_available_service_offers,
    list_owned_service_offers,
    list_received_requests,
    list_user_transactions,
    list_wallet_recharges,
    reject_request,
)
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


class PortalNotFoundError(Exception):
    # Domain-level exception so the service layer stays independent from FastAPI.
    pass


def build_portal_summary(current_user) -> PortalUserSummary:
    # Convert the authenticated user into the DTO exposed by the API.
    full_name = " ".join(part for part in [current_user.name, current_user.surname] if part).strip()
    return PortalUserSummary(
        id=current_user.id,
        name=full_name or current_user.email,
        role=current_user.role,
        email=current_user.email,
        avatar_key=current_user.avatar_key,
    )


def _build_service_offer_list(offers) -> list[ServiceOfferOut]:
    # Reuse one ORM -> DTO conversion path for every service list response.
    return [ServiceOfferOut.model_validate(item) for item in offers]


def _build_service_offer_response(offer) -> ServiceOfferOut:
    # Keep single-item service mapping aligned with list responses.
    return ServiceOfferOut.model_validate(offer)


def get_dashboard_response(db: Session, user_id: int) -> DashboardResponse:
    # Split purchasable services from owned services to support catalog tabs.
    services = _build_service_offer_list(list_available_service_offers(db, user_id))
    my_services = _build_service_offer_list(list_owned_service_offers(db, user_id))
    return DashboardResponse(services=services, my_services=my_services)


def get_history_response(db: Session, user_id: int) -> HistoryResponse:
    # Build the history response by mapping each database row into TransactionOut.
    transactions = [
        TransactionOut(
            id=item.id,
            type=item.type,
            service=item.service,
            other_user=item.other_user,
            date=(
                linked_request.scheduled_at
                if (linked_request := get_request_by_transaction_id(db, item.id)) is not None
                else format_datetime(item.occurred_at)
            ),
            address=linked_request.address if linked_request is not None else None,
            amount=item.amount,
            status=item.status,
            clarification=(
                linked_request.clarification if linked_request is not None else None
            ),
        )
        for item in list_user_transactions(db, user_id)
    ]
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
    extra: str | None,
    price: int,
    image_key: str,
) -> CreateServiceOfferResponse:
    # Create a new published service and return it ready for the frontend.
    service_offer = create_service_offer(
        db=db,
        provider=provider,
        title=title.strip(),
        description=description.strip(),
        availability=availability.strip(),
        extra=extra.strip() if extra else None,
        price=price,
        image_key=image_key.strip(),
    )
    return CreateServiceOfferResponse(
        message="Service published successfully",
        service=_build_service_offer_response(service_offer),
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
