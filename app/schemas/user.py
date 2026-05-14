"""
Define esquemas Pydantic para validar entradas y serializar respuestas.

Comentarios generados para documentar la intencion de cada bloque principal.
"""
# User-related DTOs and Pydantic validations.
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
import re


# Define esta clase y agrupa los datos que pertenecen a la entidad.
class UserCreate(BaseModel):
    email: EmailStr = Field(..., min_length=2, max_length=255, description="User email")
    password: str = Field(..., min_length=8, max_length=100, description="User password")
    name: Optional[str] = Field(None, max_length=255, description="User name")
    surname: Optional[str] = Field(None, max_length=255, description="User surname")

    # Encapsula una parte concreta de la logica de la aplicacion.
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate that the password meets the security rules."""
        if len(v) < 8:
            raise ValueError('Password must contain at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>\-_+=\[\]\\\/~`]', v):
            raise ValueError('Password must contain at least one special character')
        return v

    # Encapsula una parte concreta de la logica de la aplicacion.
    @field_validator('name', 'surname')
    @classmethod
    def validate_name_fields(cls, v: Optional[str]) -> Optional[str]:
        """Validate that names only contain letters, spaces, and accents."""
        if v is not None:
            v = v.strip()
            if not v:
                return None
            if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-]+$', v):
                raise ValueError('Only letters, spaces, and hyphens are allowed')
        return v


# Define esta clase y agrupa los datos que pertenecen a la entidad.
class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=1, max_length=100, description="User password")


# Define esta clase y agrupa los datos que pertenecen a la entidad.
class UserOut(BaseModel):
    id: int
    email: EmailStr
    name: Optional[str] = None
    surname: Optional[str] = None
    avatar_key: Optional[str] = None
    is_active: bool

    # Define esta clase y agrupa los datos que pertenecen a la entidad.
    class Config:
        from_attributes = True

# Define esta clase y agrupa los datos que pertenecen a la entidad.
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = Field(None, max_length=255, description="User email")
    name: Optional[str] = Field(None, max_length=255, description="User name")
    surname: Optional[str] = Field(None, max_length=255, description="User surname")
    avatar_key: Optional[str] = Field(None, max_length=100, description="Avatar key")

    # Encapsula una parte concreta de la logica de la aplicacion.
    @field_validator('name', 'surname')
    @classmethod
    def validate_name_fields(cls, v: Optional[str]) -> Optional[str]:
        """Validate that names only contain letters, spaces, and accents."""
        if v is not None:
            v = v.strip()
            if not v:
                return None
            if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-]+$', v):
                raise ValueError('Only letters, spaces, and hyphens are allowed')
        return v
    
# Define esta clase y agrupa los datos que pertenecen a la entidad.
class UserUpdateRole(BaseModel):
    new_role: str = Field(..., description="New role for the user")


# Define esta clase y agrupa los datos que pertenecen a la entidad.
class UserUpdateActive(BaseModel):
    is_active: bool = Field(..., description="Whether the user is active")


# Define esta clase y agrupa los datos que pertenecen a la entidad.
class UserUpdateCoins(BaseModel):
    coins: int = Field(..., ge=0, description="New wallet balance for the user")
