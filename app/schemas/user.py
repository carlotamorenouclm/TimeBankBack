from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
import re


class UserCreate(BaseModel):
    email: EmailStr = Field(..., min_length=2, max_length=255, description="User email")
    password: str = Field(..., min_length=8, max_length=100, description="User password")
    name: Optional[str] = Field(None, max_length=255, description="User name")
    surname: Optional[str] = Field(None, max_length=255, description="User surname")

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Valida que la contraseña sea segura"""
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if not re.search(r'[A-Z]', v):
            raise ValueError('La contraseña debe contener al menos una letra mayúscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('La contraseña debe contener al menos una letra minúscula')
        if not re.search(r'\d', v):
            raise ValueError('La contraseña debe contener al menos un número')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>\-_+=\[\]\\\/~`]', v):
            raise ValueError('La contraseña debe contener al menos un carácter especial')
        return v

    @field_validator('name', 'surname')
    @classmethod
    def validate_name_fields(cls, v: Optional[str]) -> Optional[str]:
        """Valida que los nombres solo contengan letras, espacios y acentos"""
        if v is not None:
            v = v.strip()
            if not v:
                return None
            if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-]+$', v):
                raise ValueError('Solo se permiten letras, espacios y guiones')
        return v


class UserOut(BaseModel):
    id: int
    email: EmailStr
    name: Optional[str] = None
    surname: Optional[str] = None
    role: str = Field(..., max_length=20)
    is_active: bool

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    surname: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None

    @field_validator('name', 'surname')
    @classmethod
    def validate_name_fields_update(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                return None
            if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-]+$', v):
                raise ValueError('Solo se permiten letras, espacios y guiones')
        return v