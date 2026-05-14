"""
Encapsula consultas y acceso a base de datos para mantener limpias las rutas.

Comentarios generados para documentar la intencion de cada bloque principal.
"""
# Database queries used by the admin panel.
from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.portal import ServiceOffer, ServiceRequest, UserWallet
from app.models.users import User
from app.db.queries_users import get_user_by_id

# Recupera la informacion solicitada desde la capa correspondiente.
def list_admins(db: Session) -> List[User]:
    return db.query(User).filter(User.role == "ADMIN").order_by(User.id.asc()).all()

# Actualiza los datos existentes con la informacion recibida.
def update_user_role(db: Session, user_id: int, new_role: str) -> Optional[User]:
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    user.role = new_role
    db.commit()
    db.refresh(user)
    return user


# Actualiza los datos existentes con la informacion recibida.
def update_user_is_active(db: Session, user_id: int, is_active: bool) -> Optional[User]:
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    user.is_active = is_active
    db.commit()
    db.refresh(user)
    return user


# Actualiza los datos existentes con la informacion recibida.
def update_user_wallet_balance(db: Session, user_id: int, coins: int) -> Optional[UserWallet]:
    user = get_user_by_id(db, user_id)
    if not user:
        return None

    wallet = db.query(UserWallet).filter(UserWallet.user_id == user_id).first()
    if wallet is None:
        wallet = UserWallet(user_id=user_id, balance=coins, status="Active")
        db.add(wallet)
    else:
        wallet.balance = coins

    db.commit()
    db.refresh(wallet)
    return wallet


# Recupera la informacion solicitada desde la capa correspondiente.
def list_user_service_offers(db: Session, user_id: int) -> List[ServiceOffer]:
    return (
        db.query(ServiceOffer)
        .filter(ServiceOffer.owner_id == user_id)
        .order_by(ServiceOffer.created_at.desc(), ServiceOffer.id.desc())
        .all()
    )


# Recupera la informacion solicitada desde la capa correspondiente.
def get_service_offer_for_admin(db: Session, service_offer_id: int) -> Optional[ServiceOffer]:
    return db.query(ServiceOffer).filter(ServiceOffer.id == service_offer_id).first()


# Actualiza los datos existentes con la informacion recibida.
def update_service_offer_visibility(
    db: Session,
    service_offer: ServiceOffer,
    is_visible: bool,
) -> ServiceOffer:
    service_offer.is_visible = is_visible
    db.commit()
    db.refresh(service_offer)
    return service_offer


# Elimina o desactiva el recurso indicado segun la regla de negocio.
def delete_service_offer_for_admin(db: Session, service_offer: ServiceOffer) -> int:
    linked_requests = (
        db.query(ServiceRequest)
        .filter(ServiceRequest.service_offer_id == service_offer.id)
        .count()
    )
    if linked_requests > 0:
        raise ValueError("Services with existing requests can only be hidden")

    deleted_service_id = service_offer.id
    db.delete(service_offer)
    db.commit()
    return deleted_service_id
