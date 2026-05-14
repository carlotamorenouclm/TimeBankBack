"""
Agrupa utilidades de seguridad, hashing y verificacion de credenciales.

Comentarios generados para documentar la intencion de cada bloque principal.
"""
# Utilidades criptograficas: hash de passwords y creacion/lectura de JWT.
from fastapi import HTTPException
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from app.core.config import settings

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# Encapsula una parte concreta de la logica de la aplicacion.
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# Comprueba credenciales, permisos o condiciones antes de continuar.
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# Crea o registra el recurso solicitado y prepara la respuesta.
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy() #copy the user data to avoid modifying the original
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire}) #add the expiration time to the token data
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

# Encapsula una parte concreta de la logica de la aplicacion.
def decode_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
