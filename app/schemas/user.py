# User-related DTOs and Pydantic validations.
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


class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=1, max_length=100, description="User password")


class UserOut(BaseModel):
    id: int
    email: EmailStr
    name: Optional[str] = None
    surname: Optional[str] = None
    avatar_key: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = Field(None, max_length=255, description="User email")
    name: Optional[str] = Field(None, max_length=255, description="User name")
    surname: Optional[str] = Field(None, max_length=255, description="User surname")
    avatar_key: Optional[str] = Field(None, max_length=100, description="Avatar key")

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
    
class UserUpdateRole(BaseModel):
    new_role: str = Field(..., description="New role for the user")
