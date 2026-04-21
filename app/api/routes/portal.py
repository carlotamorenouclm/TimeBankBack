from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.queries_portal import (
    accept_request,
    create_wallet_recharge,
    ensure_user_portal_seed_data,
    get_or_create_wallet,
    get_request_for_receiver,
    list_received_requests,
    list_service_offers,
    list_user_transactions,
    list_wallet_recharges,
    reject_request,
    seed_default_service_offers,
)
from app.db.session import get_db
from app.schemas.portal import (
    AcceptRequestPayload,
    DashboardResponse,
    HistoryResponse,
    InboxRequestOut,
    InboxResponse,
    PortalUserSummary,
    RechargePayload,
    RejectRequestPayload,
    ServiceOfferOut,
    TransactionOut,
    WalletRechargeOut,
    WalletResponse,
    format_datetime,
)

router = APIRouter()


def _bootstrap_user_data(db: Session, current_user) -> None:
    seed_default_service_offers(db)
    ensure_user_portal_seed_data(db, current_user)


@router.get("/summary", response_model=PortalUserSummary, status_code=status.HTTP_200_OK)
def get_portal_summary(current_user=Depends(get_current_user)):
    full_name = " ".join(part for part in [current_user.name, current_user.surname] if part).strip()
    return PortalUserSummary(
        id=current_user.id,
        name=full_name or current_user.email,
        role=current_user.role,
        email=current_user.email,
    )


@router.get("/dashboard", response_model=DashboardResponse, status_code=status.HTTP_200_OK)
def get_dashboard(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    _bootstrap_user_data(db, current_user)
    return DashboardResponse(services=[ServiceOfferOut.model_validate(item) for item in list_service_offers(db)])


@router.get("/history", response_model=HistoryResponse, status_code=status.HTTP_200_OK)
def get_history(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    _bootstrap_user_data(db, current_user)
    transactions = [
        TransactionOut(
            id=item.id,
            type=item.type,
            service=item.service,
            other_user=item.other_user,
            date=format_datetime(item.occurred_at),
            amount=item.amount,
            status=item.status,
        )
        for item in list_user_transactions(db, current_user.id)
    ]
    return HistoryResponse(transactions=transactions)


@router.get("/inbox", response_model=InboxResponse, status_code=status.HTTP_200_OK)
def get_inbox(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    _bootstrap_user_data(db, current_user)
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
        for item in list_received_requests(db, current_user.id)
    ]
    return InboxResponse(requests=requests)


@router.post("/inbox/{request_id}/accept", response_model=InboxResponse, status_code=status.HTTP_200_OK)
def accept_inbox_request(
    request_id: int,
    payload: AcceptRequestPayload,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    _bootstrap_user_data(db, current_user)
    request_row = get_request_for_receiver(db, request_id, current_user.id)
    if request_row is None:
        raise HTTPException(status_code=404, detail="Request not found")
    accept_request(db, request_row, payload.clarification)
    return get_inbox(db, current_user)


@router.post("/inbox/{request_id}/reject", response_model=InboxResponse, status_code=status.HTTP_200_OK)
def reject_inbox_request(
    request_id: int,
    payload: RejectRequestPayload,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    _bootstrap_user_data(db, current_user)
    request_row = get_request_for_receiver(db, request_id, current_user.id)
    if request_row is None:
        raise HTTPException(status_code=404, detail="Request not found")
    reject_request(db, request_row, payload.reason)
    return get_inbox(db, current_user)


@router.get("/wallet", response_model=WalletResponse, status_code=status.HTTP_200_OK)
def get_wallet(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    _bootstrap_user_data(db, current_user)
    wallet = get_or_create_wallet(db, current_user.id)
    recharges = [
        WalletRechargeOut(id=item.id, date=format_datetime(item.created_at), amount=item.amount)
        for item in list_wallet_recharges(db, current_user.id)
    ]
    return WalletResponse(balance=wallet.balance, status=wallet.status, recharges=recharges)


@router.post("/wallet/recharge", response_model=WalletResponse, status_code=status.HTTP_200_OK)
def recharge_wallet(
    payload: RechargePayload,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    _bootstrap_user_data(db, current_user)
    create_wallet_recharge(db, current_user.id, payload.amount)
    return get_wallet(db, current_user)
