# User portal routes: receive HTTP and delegate business logic to the service layer.
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.session import get_db
from app.schemas.portal import (
    AcceptRequestPayload,
    CreateServiceOfferPayload,
    CreateServiceOfferResponse,
    CreateServiceRequestPayload,
    CreateServiceRequestResponse,
    DashboardResponse,
    DeleteServiceOfferResponse,
    HistoryResponse,
    InboxResponse,
    PortalUserSummary,
    RechargePayload,
    RejectRequestPayload,
    WalletResponse,
)
from app.services.portal import (
    PortalNotFoundError,
    accept_inbox_request_response,
    build_portal_summary,
    create_service_offer_response,
    create_purchase_request_response,
    delete_service_offer_response,
    get_dashboard_response,
    get_history_response,
    get_inbox_response,
    get_wallet_response,
    recharge_wallet_response,
    reject_inbox_request_response,
)

router = APIRouter()


@router.get("/summary", response_model=PortalUserSummary, status_code=status.HTTP_200_OK)
def get_portal_summary(current_user=Depends(get_current_user)):
    # La ruta solo resuelve dependencias HTTP y delega el formato de salida.
    return build_portal_summary(current_user)


@router.get("/dashboard", response_model=DashboardResponse, status_code=status.HTTP_200_OK)
def get_dashboard(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # current_user protects the route even though its fields are not used here.
    return get_dashboard_response(db, current_user.id)


@router.get("/history", response_model=HistoryResponse, status_code=status.HTTP_200_OK)
def get_history(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return get_history_response(db, current_user.id)


@router.get("/inbox", response_model=InboxResponse, status_code=status.HTTP_200_OK)
def get_inbox(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return get_inbox_response(db, current_user.id)


@router.post("/inbox/{request_id}/accept", response_model=InboxResponse, status_code=status.HTTP_200_OK)
def accept_inbox_request(
    request_id: int,
    payload: AcceptRequestPayload,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        return accept_inbox_request_response(db, current_user.id, request_id, payload.clarification)
    except PortalNotFoundError as exc:
        # El servicio trabaja con errores de dominio y la ruta los traduce a HTTP.
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/inbox/{request_id}/reject", response_model=InboxResponse, status_code=status.HTTP_200_OK)
def reject_inbox_request(
    request_id: int,
    payload: RejectRequestPayload,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        return reject_inbox_request_response(db, current_user.id, request_id, payload.reason)
    except PortalNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/wallet", response_model=WalletResponse, status_code=status.HTTP_200_OK)
def get_wallet(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        return get_wallet_response(db, current_user.id)
    except PortalNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/wallet/recharge", response_model=WalletResponse, status_code=status.HTTP_200_OK)
def recharge_wallet(
    payload: RechargePayload,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        return recharge_wallet_response(db, current_user.id, payload.amount)
    except PortalNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post(
    "/services/{service_offer_id}/request",
    response_model=CreateServiceRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_service_request(
    service_offer_id: int,
    payload: CreateServiceRequestPayload,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        return create_purchase_request_response(
            db=db,
            requester=current_user,
            service_offer_id=service_offer_id,
            scheduled_at=payload.scheduled_at,
            street=payload.street,
            street_number=payload.street_number,
            floor=payload.floor,
            door=payload.door,
            message=payload.message,
        )
    except PortalNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post(
    "/services",
    response_model=CreateServiceOfferResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_service_offer(
    payload: CreateServiceOfferPayload,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        return create_service_offer_response(
            db=db,
            provider=current_user,
            title=payload.title,
            description=payload.description,
            availability=payload.availability,
            extra=payload.extra,
            price=payload.price,
            image_key=payload.image_key,
        )
    except PortalNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete(
    "/services/{service_offer_id}",
    response_model=DeleteServiceOfferResponse,
    status_code=status.HTTP_200_OK,
)
def delete_service_offer(
    service_offer_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        return delete_service_offer_response(db, current_user.id, service_offer_id)
    except PortalNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
