"""
Expone endpoints HTTP y adapta peticiones/respuestas del dominio.

Comentarios generados para documentar la intencion de cada bloque principal.
"""
# Routes related to the currently authenticated user.
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import UserOut, UserPasswordUpdate, UserUpdate
from app.core.auth import get_current_user
from app.core.security import verify_password
from app.db.queries_users import (
    delete_user_account,
    get_user_by_email,
    update_password,
    update_user,
)

router = APIRouter()

# Encapsula una parte concreta de la logica de la aplicacion.
@router.get("", response_model=UserOut, status_code=status.HTTP_200_OK)
def me(current_user=Depends(get_current_user)):
    return current_user


# Actualiza los datos existentes con la informacion recibida.
@router.post("/update", response_model=UserOut, status_code=status.HTTP_200_OK)
def update_me(
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if payload.email and payload.email != current_user.email:
        existing_user = get_user_by_email(db, payload.email)
        if existing_user:
            raise HTTPException(status_code=409, detail="Email already registered")

    user = update_user(
        db,
        current_user.id,
        email=payload.email,
        name=payload.name,
        surname=payload.surname,
        avatar_key=payload.avatar_key,
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# Actualiza la contrasena del usuario autenticado tras verificar la actual.
@router.post("/password", status_code=status.HTTP_200_OK)
def update_my_password(
    payload: UserPasswordUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    if verify_password(payload.new_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="New password must be different")

    user = update_password(db, current_user.id, payload.new_password)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Password updated successfully"}


# Elimina o desactiva el recurso indicado segun la regla de negocio.
@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
def delete_me(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    ok = delete_user_account(db, current_user)
    if not ok:
        raise HTTPException(status_code=404, detail="User not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Encapsula una parte concreta de la logica de la aplicacion.
@router.post("/isAdmin", response_model=bool, status_code=status.HTTP_200_OK)
def is_admin(current_user=Depends(get_current_user)):
    return current_user.role == "ADMIN"
